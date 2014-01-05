##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import ularch_bottle_app


# Set this to change the path in which U-Larch will look for files
DOCUMENTS_PATH = None

# Set this to change the directoyr in which U-Larch will look for documentation
DOCUMENTATION_PATH = None


app = ularch_bottle_app.make_ularch_bottle_app(docpath=DOCUMENTS_PATH, documentation_path=DOCUMENTATION_PATH)
