from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from app.models import Testimonial

testimonials_ns = Namespace('testimonials', description='Testimonial operations')

testimonial_model = testimonials_ns.model('Testimonial', {
    'id': fields.Integer(readonly=True),
    'user_id': fields.Integer(required=True),
    'space_id': fields.Integer(required=True),
    'rating': fields.Integer(required=True),
    'comment': fields.String(required=True)
})

@testimonials_ns.route('/')
class TestimonialList(Resource):
    @testimonials_ns.marshal_list_with(testimonial_model)
    def get(self):
        """Get all testimonials"""
        return Testimonial.query.all()

    @jwt_required()
    @testimonials_ns.expect(testimonial_model)
    @testimonials_ns.response(201, 'Testimonial created successfully')
    def post(self):
        """Create a new testimonial"""
        data = request.get_json()
        current_user_id = get_jwt_identity()
        testimonial = Testimonial(user_id=current_user_id, **data)
        testimonial.save()
        return {'message': 'Testimonial created successfully'}, 201

@testimonials_ns.route('/<int:testimonial_id>')
class TestimonialDetail(Resource):
    @testimonials_ns.marshal_with(testimonial_model)
    def get(self, testimonial_id):
        """Get testimonial details"""
        return Testimonial.query.get_or_404(testimonial_id)

    @jwt_required()
    def delete(self, testimonial_id):
        """Delete a testimonial"""
        testimonial = Testimonial.query.get_or_404(testimonial_id)
        current_user_id = get_jwt_identity()
        if testimonial.user_id != current_user_id:
            return {'message': 'Unauthorized'}, 403
        testimonial.delete()
        return {'message': 'Testimonial deleted successfully'}
