# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Course Builder web application entry point."""

__author__ = 'Pavel Simakov (psimakov@google.com)'

import os

import webapp2

# The following import is needed in order to add third-party libraries.
import appengine_config  # pylint: disable=unused-import

from common import users
from controllers import sites
from models import analytics
from models import custom_modules
from models import data_sources


# Set the default users service before we do anything else.
users.UsersServiceManager.set(users.AppEnginePassthroughUsersService)

# Import, register, & enable modules named in app.yaml's GCB_REGISTERED_MODULES.
appengine_config.import_and_enable_modules()

# Core "module" is always present and registered.
custom_modules.register_core_module(
    analytics.get_global_handlers(),
    analytics.get_namespaced_handlers() +
    data_sources.get_namespaced_handlers())

# Collect routes (URL-matching regexes -> handler classes) for modules.
global_routes, namespaced_routes = custom_modules.Registry.get_all_routes()

# Configure routes available at '/%namespace%/' context paths
sites.ApplicationRequestHandler.bind(namespaced_routes)
app_routes = [(r'(.*)', sites.ApplicationRequestHandler)]

# enable Appstats handlers if requested
appstats_routes = []
if appengine_config.gcb_appstats_enabled():
    import google.appengine.ext.appstats.ui as appstats_ui

    # add all Appstats URL's to /admin/stats basepath
    for path, handler in appstats_ui.URLMAP:
        assert '.*' == path[:2]
        appstats_routes.append(('/admin/stats/%s' % path[3:], handler))

# i18n configuration for jinja2
webapp2_i18n_config = {'translations_path': os.path.join(
    appengine_config.BUNDLE_ROOT, 'modules/i18n/resources/locale')}

# init application
app = webapp2.WSGIApplication(
    global_routes + appstats_routes + app_routes,
    config={'webapp2_extras.i18n': webapp2_i18n_config},
    debug=not appengine_config.PRODUCTION_MODE)
