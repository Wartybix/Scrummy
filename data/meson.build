conf = configuration_data()
conf.set('ICON', APPLICATION_ID)
conf.set('APPLICATION_ID', APPLICATION_ID)
conf.set('PREFIX', PREFIX)
conf.set('bindir', get_option('prefix') / get_option('bindir'))

desktop_file = i18n.merge_file(
        input: configure_file(
          input: 'io.github.wartybix.Scrummy.desktop.in',
          output: APPLICATION_ID + '.desktop.in',
          configuration: conf
        ),
       output: APPLICATION_ID + '.desktop',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'applications'
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

appstream_file = i18n.merge_file(
        input: configure_file(
          input: 'io.github.wartybix.Scrummy.metainfo.xml.in',
          output: APPLICATION_ID + '.metainfo.xml.in',
          configuration: conf
        ),
       output: APPLICATION_ID + '.metainfo.xml',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'metainfo'
)

appstreamcli = find_program('appstreamcli', required: false, disabler: true)
test('Validate appstream file', appstreamcli,
     args: ['validate', '--no-net', '--explain', appstream_file])

install_data(
  configure_file(
    input: 'io.github.wartybix.Scrummy.gschema.xml.in',
    output: APPLICATION_ID + '.gschema.xml',
    configuration: conf
  ),
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

compile_schemas = find_program('glib-compile-schemas', required: false, disabler: true)
test('Validate schema file',
     compile_schemas,
     args: ['--strict', '--dry-run', meson.current_source_dir()])


configure_file(
  input: 'io.github.wartybix.Scrummy.service.in',
  output: APPLICATION_ID + '.service',
  configuration: conf,
  install_dir: get_option('datadir') / 'dbus-1' / 'services'
)

subdir('icons')
