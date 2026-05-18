from flask import Flask, render_template

app = Flask(

    __name__,

    template_folder='statics/templates',

    static_folder='statics'

)