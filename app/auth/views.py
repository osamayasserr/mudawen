from . import auth
from .forms import (LoginForm, RegistrationForm, ChangePasswordForm,
                    RequestPasswordResetForm, ResetPasswordForm, ChangeEmailForm)
from ..models import User
from .. import db
from ..email import send_email
from flask import render_template, request, flash, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user
from ..decorators import requires_confirmation


# Redirects the user to the unconfirmed page
@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next = request.args.get('next')
            if not next or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Email Confirmation',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed you account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Email Confirmation',
               '/auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
@requires_confirmation
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db.session.add(current_user)
        db.session.commit()
        flash('Password updated! Please login.')
        return redirect(url_for('auth.logout'))
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def request_password_reset():
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_password_reset_token()
        send_email(user.email, 'Password Reset',
                   '/auth/email/reset_password', user=user, token=token)
        flash(f'An email with instructions has been sent to: {user.email}')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.new_password.data):
            db.session.commit()
            flash('Password updated successfully!')
        else:
            flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
@requires_confirmation
def request_email_change():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.new_email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(form.new_email.data, 'Confirm your email address',
                       '/auth/email/change_email', user=current_user, token=token)
            flash(
                f'An email with instructions has been sent to: {form.new_email.data}')
            return redirect(url_for('main.index'))
        flash('Invalid password.')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('Email updated successfully!')
        return redirect(url_for('auth.logout'))
    flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))
