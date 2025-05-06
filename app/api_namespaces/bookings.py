from flask_restx import Namespace, Resource

bookings_ns = Namespace('bookings', description='Booking operations')

# Add minimal stub resource to avoid import errors
@bookings_ns.route('/')
class BookingList(Resource):
    def get(self):
        return {'message': 'Booking list stub'}
