pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'scrummy'
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    'shortcuts-dialog.blp',
    'window.blp',
    'ingredient_row.blp',
    'new_meal_dialog.blp',
    'new_ingredient_dialog.blp'
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version() + VCS_TAG)
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)
conf.set('PREFIX', PREFIX)
conf.set('APPLICATION_ID', APPLICATION_ID)

gnome.compile_resources('scrummy',
  configure_file(
    input: 'scrummy.gresource.xml.in',
    output: 'scrummy.gresource.xml',
    configuration: conf
  ),
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints
)

configure_file(
  input: 'scrummy.in',
  output: 'scrummy',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

scrummy_sources = [
  configure_file(
    input: '__init__.py.in',
    output: '__init__.py',
    configuration: conf
  ),
  'main.py',
  'window.py',
  'ingredient_row.py',
  'new_meal_dialog.py',
  'new_ingredient_dialog.py',
  'meal.py'
]

install_data(scrummy_sources, install_dir: moduledir)
