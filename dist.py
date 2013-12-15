import os, glob, sys, py_compile, zipfile, subprocess
from optparse import OptionParser

ularch_files = [
	'Shell.ularch',
]

usage = "usage: %prog [options] <version>"
op_parser = OptionParser(usage)
op_parser.add_option('-d', '--distribution', dest='distribution', help='Distribution (everything|publicbin) default=everything', default='publicbin')

options, args = op_parser.parse_args()

if len(args) != 1:
	op_parser.error('You didn\'t supply a version')
	sys.exit( 0 )
else:
	version_string = args[0]

distribution = options.distribution

if distribution != 'everything'  and  distribution != 'publicbin':
	op_parser.error('Unknown distribution {0}'.format(distribution))
	sys.exit(0)




bin_zip_filename = 'UbiquitousLarch-' + version_string + '.zip'
package_name = 'UbiquitousLarch-' + version_string

ignore_list = [ '.hg' ]

tmp_pyc_file = 'tmp.pyc'
tmp_js_min_file = 'tmp.min.js'









dirs_for_copy = [
	( 'static', '*.*' ),
	( 'docs', '*.*' ),
	( 'testimages', '*.*' ),
	]

dirs_excluded_from_copy = [
	os.path.join('static', 'lightbox'),
]

dirs_for_compile = ['larch']

dirs_for_minify = [
	os.path.join('static', 'larch')
]


everything_root_files = [
	'server_cherrypy.py',
	'server_flask.py',
	'django_app.py',
	'django_settings.py',
	'django_urls.py',
	'django_wsgi.py',
	'manage.py',
]


root_files = [
	'bottle.py',
	'start_ularch.py',
	'LICENSE-*.txt',
	'README.txt',
] + ularch_files + (everything_root_files   if distribution == 'everything'   else [])



everything_root_compile_files = [
	'django_app.py',
	'django_settings.py',
	'django_urls.py',
	'django_wsgi.py',
]

root_compile_files = [
	'bottle.py',
] + (everything_root_compile_files   if distribution == 'everything'   else [])


def copy_file(z, src, dst):
	z.write( src, dst )


def copy_root_files(z, destDir):
	for name in root_files:
		for fname in glob.glob(name):
			destPath = os.path.join(destDir, fname)
			z.write(fname, destPath)


def copy_dir(z, src, dst, patterns, exclusions):
	if src not in exclusions:
		for e in os.listdir( src ):
			s = os.path.join( src, e )
			if os.path.isdir( s ):
				if e not in ignore_list:
					copy_dir(z, os.path.join( src, e ), os.path.join( dst, e ), patterns, exclusions)

		for pattern in patterns:
			for s in glob.glob( os.path.join( src, pattern ) ):
				if os.path.isfile( s ):
					filename = os.path.basename( s )
					d = os.path.join( dst, filename )

					copy_file( z, s, d )
	else:
		print 'EXCLUDING directory {0} from copying'.format(src)

def compile_file(z, src, dst):
	py_compile.compile( src, tmp_pyc_file )
	z.write( tmp_pyc_file, dst )


def compile_dir(z, src, dst):
	for e in os.listdir( src ):
		s = os.path.join( src, e )
		if os.path.isdir( s ):
			if e not in ignore_list:
				compile_dir( z, os.path.join( src, e ), os.path.join( dst, e ) )

	for s in glob.glob( os.path.join( src, '*.py' ) ):
		if os.path.isfile( s ):
			filename = os.path.basename( s )
			name, ext = os.path.splitext(filename)
			dest_filename = name + '.pyc'
			d = os.path.join( dst, dest_filename )

			compile_file( z, s, d )


def minify_file(z, src, dst):
	subprocess.call(['java', '-jar', '/packages/closure-compiler/compiler.jar', '--compilation_level', 'WHITESPACE_ONLY', '--js', os.path.abspath(src), '--js_output_file', tmp_js_min_file])
	z.write( tmp_js_min_file, dst )


def minify_dir(z, src, dst):
	for e in os.listdir( src ):
		s = os.path.join( src, e )
		if os.path.isdir( s ):
			if e not in ignore_list:
				minify_dir( z, os.path.join( src, e ), os.path.join( dst, e ) )
		elif os.path.isfile(s):
			filename = os.path.basename( s )
			name, ext = os.path.splitext(filename)
			ext = ext.lower()
			d = os.path.join(dst, filename)
			if ext == '.js':
				minify_file( z, s, d )
			else:
				copy_file( z, s, d )



print 'Binary package: {0}'.format( bin_zip_filename )
bin_zip = zipfile.ZipFile( bin_zip_filename, 'w', zipfile.ZIP_DEFLATED )

print 'Adding files in root directory'
copy_root_files( bin_zip, package_name )


for d in dirs_for_copy:
	print 'Adding files in {0}'.format( d[0] )
	copy_dir( bin_zip, d[0], os.path.join( package_name, d[0] ), d[1:], dirs_for_minify + dirs_excluded_from_copy )

for d in dirs_for_compile:
	print 'Compiling files in {0}'.format( d )
	compile_dir( bin_zip, d, os.path.join( package_name, d ) )

for d in dirs_for_minify:
	print 'Minifying files in {0}'.format( d )
	minify_dir( bin_zip, d, os.path.join( package_name, d ) )


for s in root_compile_files:
	d = os.path.splitext(s)[0] + '.pyc'
	d = os.path.join(package_name, d)
	compile_file(bin_zip, s, d)

if os.path.exists( tmp_pyc_file ):
	os.remove( tmp_pyc_file )

bin_zip.close()
