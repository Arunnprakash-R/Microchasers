from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.main import bp
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.main import bp
from app.main.forms import SampleForm, ImageUploadForm
from app.models import Sample, Image, Detection
from app.database import db
from app.services.image_processing import detect_microplastics

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    samples = current_user.samples.order_by(Sample.timestamp.desc()).all()
    return render_template('index.html', title='Home', samples=samples)

@bp.route('/create_sample', methods=['GET', 'POST'])
@login_required
def create_sample():
    form = SampleForm()
    if form.validate_on_submit():
        sample = Sample(name=form.name.data, author=current_user)
        db.session.add(sample)
        db.session.commit()
        flash('Your sample has been created!')
        return redirect(url_for('main.index'))
    return render_template('create_sample.html', title='Create Sample', form=form)

@bp.route('/sample/<int:id>', methods=['GET', 'POST'])
@login_required
def sample(id):
    sample = Sample.query.get_or_404(id)
    if sample.author != current_user:
        flash('You are not authorized to view this sample.')
        return redirect(url_for('main.index'))

    form = ImageUploadForm()
    if form.validate_on_submit():
        f = form.image.data
        filename = secure_filename(f.filename)
        upload_path = os.path.join(current_app.root_path, 'static/uploads', filename)
        f.save(upload_path)

        # Create a new image record
        new_image = Image(filepath=f'uploads/{filename}', sample=sample)
        db.session.add(new_image)
        db.session.commit()

        # Process the image
        detections, processed_image_path = detect_microplastics(upload_path)

        # Update image record with the path to the processed image
        if processed_image_path:
            processed_filename = os.path.basename(processed_image_path)
            new_image.filepath = f'uploads/{processed_filename}'

        # Save detections
        for det in detections:
            detection = Detection(
                x_coordinate=det['x'],
                y_coordinate=det['y'],
                confidence=det['confidence'],
                image=new_image
            )
            db.session.add(detection)

        db.session.commit()

        flash('Image uploaded and processed successfully!')
        return redirect(url_for('main.sample', id=id))

    images = sample.images.order_by(Image.timestamp.desc()).all()
    return render_template('sample.html', title=sample.name, sample=sample, form=form, images=images)

@bp.route('/samples')
@login_required
def samples():
    samples = current_user.samples.order_by(Sample.timestamp.desc()).all()
    return render_template('samples.html', title='My Samples', samples=samples)
