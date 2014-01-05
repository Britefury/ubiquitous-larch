##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import ularch_bottle_app


#
# SETTINGS
#



# WARNING: By modifying the GLOBAL_PASSWORD setting you understand the security implications and
# accept full responsibility and liability for any damages or events that occur as a result of
# the use of this software. The author(s) accept no liability for anything that results
# from the use of this software.

# Put a password within the quotes to enable the collaborative server
GLOBAL_PASSWORD = ''

# WARNING: By modifying the GLOBAL_PASSWORD setting you understand the security implications and
# accept full responsibility and liability for any damages or events that occur as a result of
# the use of this software. The author(s) accept no liability for anything that results
# from the use of this software.




# Set this to change the path in which U-Larch will look for files
DOCUMENTS_PATH = None

# Set this to change the directoyr in which U-Larch will look for documentation
DOCUMENTATION_PATH = None



#
# CREATE THE APP
#

app = ularch_bottle_app.make_ularch_bottle_app(docpath=DOCUMENTS_PATH, documentation_path=DOCUMENTATION_PATH, password=GLOBAL_PASSWORD)
