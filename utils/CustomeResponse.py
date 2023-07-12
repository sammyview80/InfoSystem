from rest_framework.response import Response


class CustomeResponse(Response):
    def __init__(self, data, **args):
        print(args, data)
        response = super().__init__({
            'status': args.get('status', 200),
            'message': data['message'],
            'data': data['data']
        }, **args)
        return response
