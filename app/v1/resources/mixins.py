

class GetPayloadMixIn:

    def get_payload(self, ns, model):
        @ns.marshal_with(model)
        def get_request():
            return ns.payload
        return get_request()

    def get_payload_update(self, ns, model,**kwargs):
        @ns.marshal_with(model,**kwargs)
        def get_request():
            return ns.payload
        return get_request()