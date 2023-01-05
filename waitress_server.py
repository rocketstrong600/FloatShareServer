from waitress import serve
from  FloatREST import app
serve(app, host='0.0.0.0', port=4343)
