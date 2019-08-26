
def pygamewindow(term):
    from pyconsolegraphics.backends.pygame import PygameWindowBackend
    return PygameWindowBackend(term)


def pygamesurface(term):
    from pyconsolegraphics.backends.pygame import PygameSurfaceBackend
    return PygameSurfaceBackend(term)

#A dict of functions that take one argument, a Terminal, and return a backend
#object
backend_funcs={
    "pygamewindow": pygamewindow,
    "pygamesurface": pygamesurface
}