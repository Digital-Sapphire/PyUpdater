# -*- coding: utf-8 -*-
from __future__ import print_function

"""Minimal API documentation generation."""

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import inspect

try:
    from inspect import getfullargspec as getargspec
except ImportError:
    from inspect import getargspec
import os
import os.path as op
import re
import sys

from six import string_types

sys.path.append(os.getcwd())


# ------------------------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------------------------


def _name(obj):
    if hasattr(obj, "__name__"):
        return obj.__name__
    elif inspect.isdatadescriptor(obj):
        return obj.fget.__name__


def _full_name(subpackage, obj):
    return "{}.{}".format(subpackage.__name__, _name(obj))


def _anchor(name):
    anchor = name.lower().replace(" ", "-")
    anchor = re.sub(r"[^\w\- ]", "", anchor)
    return anchor


_docstring_header_pattern = re.compile(
    r"^([^\n]+)\n[\-\=]{3,}$",
    flags=re.MULTILINE,
)
_docstring_parameters_pattern = re.compile(
    r"^([^ \n]+) \: ([^\n]+)$",
    flags=re.MULTILINE,
)


def _replace_docstring_header(paragraph):
    """Process NumPy-like function docstrings."""

    # Replace Markdown headers in docstrings with light headers in bold.
    paragraph = re.sub(
        _docstring_header_pattern,
        r"*\1*",
        paragraph,
    )

    paragraph = re.sub(
        _docstring_parameters_pattern,
        r"\n* `\1` (\2)\n",
        paragraph,
    )

    return paragraph


def _doc(obj):
    doc = inspect.getdoc(obj) or ""
    doc = doc.strip()
    if doc and "---" in doc:
        return _replace_docstring_header(doc)
    else:
        return doc


def _import_module(module_name):
    """
    Imports a module. A single point of truth for importing modules to
    be documented by `pdoc`. In particular, it makes sure that the top
    module in `module_name` can be imported by using only the paths in
    `pdoc.import_path`.

    If a module has already been imported, then its corresponding entry
    in `sys.modules` is returned. This means that modules that have
    changed on disk cannot be re-imported in the same process and have
    its documentation updated.
    """
    import_path = sys.path[:]
    if import_path != sys.path:
        # Such a kludge. Only restrict imports if the `import_path` has
        # been changed. We don't want to always restrict imports, since
        # providing a path to `imp.find_module` stops it from searching
        # in special locations for built ins or frozen modules.
        #
        # The problem here is that this relies on the `sys.path` not being
        # independently changed since the initialization of this module.
        # If it is changed, then some packages may fail.
        #
        # Any other options available?

        # Raises an exception if the parent module cannot be imported.
        # This hopefully ensures that we only explicitly import modules
        # contained in `pdoc.import_path`.
        imp.find_module(module_name.split(".")[0], import_path)

    if module_name in sys.modules:
        return sys.modules[module_name]
    else:
        __import__(module_name)
        return sys.modules[module_name]


# ------------------------------------------------------------------------------
# Introspection methods
# ------------------------------------------------------------------------------


def _is_public(obj):
    name = _name(obj) if not isinstance(obj, string_types) else obj
    if name:
        return not name.startswith("_")
    else:
        return True


def _is_defined_in_package(obj, package):
    if isinstance(obj, property):
        obj = obj.fget
    mod = inspect.getmodule(obj)
    if mod and hasattr(mod, "__name__"):
        name = mod.__name__
        return name.split(".")[0] == package
    return True


def _iter_doc_members(obj, package=None):
    for _, member in inspect.getmembers(obj):
        if _is_public(member):
            if package is None or _is_defined_in_package(member, package):
                yield member


def _iter_subpackages(package, subpackages):
    """Iterate through a list of subpackages."""
    for subpackage in subpackages:
        yield _import_module("{}.{}".format(package, subpackage))


def _iter_vars(mod):
    """Iterate through a list of variables define in a module's
    public namespace."""
    _vars = sorted(var for var in dir(mod) if _is_public(var))
    for var in _vars:
        yield getattr(mod, var)


def _iter_functions(subpackage):
    return filter(inspect.isfunction, _iter_vars(subpackage))


def _iter_classes(subpackage):
    return filter(inspect.isclass, _iter_vars(subpackage))


def _iter_methods(klass, package=None):
    for member in _iter_doc_members(klass, package):
        if inspect.isfunction(member) or inspect.ismethod(member):
            if inspect.isdatadescriptor(member):
                continue
            yield member


def _iter_properties(klass, package=None):
    for member in _iter_doc_members(klass, package):
        if isinstance(member, property):
            yield member.fget


# ------------------------------------------------------------------------------
# API doc generation
# ------------------------------------------------------------------------------


def _concat(header, docstring):
    return "{header}\n\n{docstring}".format(
        header=header,
        docstring=docstring,
    )


def _function_header(subpackage, func):
    """Generate the docstring of a function."""
    args = inspect.formatargspec(*getargspec(func))
    return "{name}{args}".format(
        name=_full_name(subpackage, func),
        args=args,
    )


def _doc_function(subpackage, func):
    return _concat(
        _function_header(subpackage, func),
        _doc(func),
    )


def _doc_method(klass, func):
    """Generate the docstring of a method."""
    argspec = inspect.getargspec(func)
    # Remove first 'self' argument.
    if argspec.args and argspec.args[0] == "self":
        del argspec.args[0]
    args = inspect.formatargspec(*argspec)
    header = "{klass}.{name}{args}".format(
        klass=klass.__name__,
        name=_name(func),
        args=args,
    )
    docstring = _doc(func)
    return _concat(header, docstring)


def _doc_property(klass, prop):
    """Generate the docstring of a property."""
    header = "{klass}.{name}".format(
        klass=klass.__name__,
        name=_name(prop),
    )
    docstring = _doc(prop)
    return _concat(header, docstring)


def _link(name, anchor=None):
    return "[{name}](#{anchor})".format(
        name=name,
        anchor=anchor or _anchor(name),
    )


def _generate_preamble(package, subpackages):
    yield "# API"

    yield _doc(_import_module(package))

    yield "## Table of contents"

    # Table of contents: list of modules.
    for subpackage in _iter_subpackages(package, subpackages):
        subpackage_name = subpackage.__name__

        yield "### " + _link(subpackage_name)

        # List of top-level functions in the subpackage.
        for func in _iter_functions(subpackage):
            yield "* " + _link(
                _full_name(subpackage, func),
                _anchor(_function_header(subpackage, func)),
            )

        # All public classes.
        for klass in _iter_classes(subpackage):
            # Class documentation.
            yield "* " + _link(_full_name(subpackage, klass))

        yield ""

    yield ""


def _generate_paragraphs(package, subpackages):
    """Generate the paragraphs of the API documentation."""

    # API doc of each module.
    for subpackage in _iter_subpackages(package, subpackages):
        subpackage_name = subpackage.__name__

        yield "## {}".format(subpackage_name)

        # Subpackage documentation.
        yield _doc(_import_module(subpackage_name))

        # List of top-level functions in the subpackage.
        for func in _iter_functions(subpackage):
            yield "##### " + _doc_function(subpackage, func)

        # All public classes.
        for klass in _iter_classes(subpackage):

            # Class documentation.
            yield "### {}".format(_full_name(subpackage, klass))
            yield _doc(klass)

            yield "#### Methods"
            for method in _iter_methods(klass, package):
                yield "##### " + _doc_method(klass, method)

                # Uncomment to document properties.
                # yield "#### Properties"
                # for prop in _iter_properties(klass, package):
                #     yield '##### ' + _doc_property(klass, prop)


def _print_paragraph(paragraph):
    out = ""
    out += paragraph + "\n"
    if not paragraph.startswith("* "):
        out += "\n"
    return out


def generate_api_doc(package, subpackages, path=None):
    out = ""
    for paragraph in _generate_preamble(package, subpackages):
        out += _print_paragraph(paragraph)
    for paragraph in _generate_paragraphs(package, subpackages):
        out += _print_paragraph(paragraph)
    if path is None:
        return out
    else:
        with open(path, "w") as f:
            f.write(out)


def main():
    package = "pyupdater"
    subpackages = [
        # 'cli',
        "client",
        # 'hooks',
        # 'core.key_handler',
        # 'core.package_handler',
        # 'utils',
    ]

    curdir = op.dirname(op.realpath(__file__))
    path = op.join(curdir, "../docs/api.md")
    generate_api_doc(package, subpackages, path=path)


if __name__ == "__main__":
    main()
