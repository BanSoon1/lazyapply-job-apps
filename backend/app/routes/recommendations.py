from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.recommendation_service import get_recommendations

recommendations_bp = Blueprint("recommendations", __name__, url_prefix="/api")


@recommendations_bp.get("/recommendations")
@jwt_required()
def recommendations():
    user_id = int(get_jwt_identity())
    result, status = get_recommendations(user_id)
    return jsonify(result), status