import season
import pypugjs
import sass

for key in wiz.request.segment:
    kwargs[key] = wiz.request.segment[key]

mode = wiz.request.segment.mode
namespace = wiz.request.segment.namespace
stage_id = wiz.request.segment.stage_id

dizest = wiz.model("dizest").load(namespace, mode=mode)
workspace = dizest.workspace()
stage = workspace.stage[stage_id]

pug = stage.get("pug")
pugconfig = season.stdClass()
pugconfig.variable_start_string = '{$'
pugconfig.variable_end_string = '$}'
pug = pypugjs.Parser(pug)
pug = pug.parse()
pug = pypugjs.ext.jinja.Compiler(pug, **pugconfig).compile()

js = stage.get("js")

css = stage.get("css")
css = ".dizest-app { " + css + " }"
css = sass.compile(string=css)
css = str(css)

view = f"<script type='text/javascript'>{js}</script><style>{css}</style>{pug}"
kwargs['view'] = view