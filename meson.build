project('spacebeam',
          version: '0.1.0',
    meson_version: '>= 0.50.0',
  default_options: [ 'warning_level=2',
                   ],
)

i18n = import('i18n')

dependency('gtk+-3.0', version: '>= 3.22')
dependency('glib-2.0')
dependency('libsoup-2.4')

subdir('data')
subdir('src')
subdir('po')

meson.add_install_script('build-aux/meson/postinstall.py')
