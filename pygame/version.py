# pygame_cffi - a cffi implementation of the pygame library
# Copyright (C) 2016  Neil Muller
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301  USA

#
# We hardcode the version number and beta level to match recent pygame trunk.
# This needs to be updated manually

ver = '1.9.2b8'
# We could extract this from version, as pygame does at build time, but that seems
# overly complicated.
vernum = (1, 9, 2)
# This should be updated before releasing
pygame_cffi_version = '0.2.0'
