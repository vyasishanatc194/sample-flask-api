from flask_restplus import reqparse, inputs
from .authorizations import get_jwt_detail


auth_refresh_token_header_parser = reqparse.RequestParser()
auth_refresh_token_header_parser.add_argument('Authorization', type=str, location='headers', required=True)

user_detail={
    "user_claims":{"country":"CA"
    }
}
def get_request_argument():
    print(f"get_request_argument")
    parser = reqparse.RequestParser()
    # user_detail = get_jwt_detail()
    print(f"country: {user_detail.get('user_claims', {}).get('country', 'CA')}")
    parser.add_argument('country', type=str, default=user_detail.get('user_claims', {}).get('country', 'CA'),
                        help='Country', location="args")
    parser.add_argument('limit', type=int, default=10, help='limit', location="args")
    parser.add_argument('offset', type=int, default=0, help='Offset', location="args")
    parser.add_argument('search', type=str, default=None, help='Search Text', location="args")
    parser.add_argument('formatted', type=inputs.boolean, default=False, help='Formatted', location="args")
    parser.add_argument('provider_code_equality', type=inputs.boolean, default=False,
                        help='Provider Code', location="args",)
    parser.add_argument('procedure_code', type=int, default=0, help='procedure code', location="args")
    parser.add_argument('profile_name', type=str, default=None, help='profile name', location="args")
    args = parser.parse_args()
    return args


npi_request_parser = reqparse.RequestParser()
# user_detail = get_jwt_detail()
npi_request_parser.add_argument('search', type=str, default=None, help='Search Text', location="args")
npi_request_parser.add_argument('limit', type=int, default=10, help='limit', location="args")
npi_request_parser.add_argument('offset', type=int, default=0, help='Offset', location="args")
npi_request_parser.add_argument('formatted', type=inputs.boolean, default=False, help='Formatted', location="args")
npi_request_parser.add_argument('country', type=str, default=user_detail.get('user_claims', {}).get('country', 'CA'),
                    help='Country', location="args")
npi_request_parser.add_argument('provider_code_equality', type=inputs.boolean, default=False,
                    help='Provider Code', location="args",)


insurance_request_parser = reqparse.RequestParser()
# user_detail = get_jwt_detail()
insurance_request_parser.add_argument('search', type=str, default=None, help='Search Text', location="args")
insurance_request_parser.add_argument('country', type=str, default=user_detail.get('user_claims', {}).get('country', 'CA'),
                    help='Country', location="args")
insurance_request_parser.add_argument('limit', type=int, default=10, help='limit', location="args")
insurance_request_parser.add_argument('offset', type=int, default=0, help='Offset', location="args")


pharmacy_request_parser = reqparse.RequestParser()
# user_detail = get_jwt_detail()
pharmacy_request_parser.add_argument('search', type=str, default=None, help='Search Text', location="args")
pharmacy_request_parser.add_argument('country', type=str, default=user_detail.get('user_claims', {}).get('country', 'CA'),
                    help='Country', location="args")
pharmacy_request_parser.add_argument('limit', type=int, default=10, help='limit', location="args")
pharmacy_request_parser.add_argument('offset', type=int, default=0, help='Offset', location="args")


pricing_request_parser = reqparse.RequestParser()
pricing_request_parser.add_argument('procedure_code', type=int, default=0, help='procedure code', location="args")
pricing_request_parser.add_argument('profile_name', type=str, default=None, help='profile name', location="args")
pricing_request_parser.add_argument('limit', type=int, default=10, help='limit', location="args")
pricing_request_parser.add_argument('offset', type=int, default=0, help='Offset', location="args")


procedure_request_parser = reqparse.RequestParser()
# user_detail = get_jwt_detail()
procedure_request_parser.add_argument('search', type=str, default=None, help='Search Text', location="args")
procedure_request_parser.add_argument('limit', type=int, default=10, help='limit', location="args")
procedure_request_parser.add_argument('offset', type=int, default=0, help='Offset', location="args")
procedure_request_parser.add_argument('formatted', type=inputs.boolean, default=False, help='Formatted', location="args")
procedure_request_parser.add_argument('country', type=str, default=user_detail.get('user_claims', {}).get('country', 'CA'),
                    help='Country', location="args")