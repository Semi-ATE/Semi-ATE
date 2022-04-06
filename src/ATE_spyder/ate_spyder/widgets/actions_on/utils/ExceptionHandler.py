from enum import Enum


def generate_exception(text, title, is_trace_back, label, steps, repo='Semi-ATE/Semi-ATE'):
    return {"text": text,
            "is_traceback": is_trace_back,
            "repo": repo,
            "title": title,
            "label": label,
            "steps": steps}


def report_exception(parent, title, is_trace_back=True, label='', steps=''):
    import traceback
    text = traceback.format_exc()
    parent.sig_exception_occurred.emit(generate_exception(text, title, is_trace_back, label, steps))


def handle_excpetions(parent, call_back_function, call_back_source):
    try:
        call_back_function()
    except Exception:
        from ate_spyder.widgets.actions_on.utils.ExceptionHandler import report_exception
        report_exception(parent, call_back_source)


class ExceptionTypes(Enum):
    Maskset = 'maskset wizard exception'
    Hardware = 'hardware wizard exception'
    Die = 'die wizard exception'
    Package = 'package wizard exception'
    Device = 'device wizard exception'
    Product = 'product wizard exception'
    Test = 'test wizard exception'
    Program = 'program wizard exception'
    Protocol = 'protocol wizard exception'

    def __call__(self):
        return self.value
