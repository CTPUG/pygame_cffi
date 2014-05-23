TODO
====

Contributions are welcome! Most important things that need doing:

* implement subsurface locking (check for PySurface_Prep/Unprep in C)
* implement all [transform](./blob/master/pygame/transform.py) functions
* implement all [draw](./blob/master/pygame/draw.py) functions
* fix failing tests (total = 227, failures = 6, errors = 24 - often NotImplementedError)
* implement "todo_" tests (e.g. [this one](https://github.com/CTPUG/pygame_cffi/blob/master/test/draw_test.py#L149))
* improve test coverage in general
* implement [BufferProxy](http://www.pygame.org/docs/ref/bufferproxy.html)
* implement [surfarray](http://www.pygame.org/docs/ref/surfarray.html)
