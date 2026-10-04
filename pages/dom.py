"""Small DOM helpers shared by the page objects.

Native HTML date/datetime-local controls render a locale-sensitive picker
widget rather than a plain text box, so ``send_keys`` behavior is not
reliable across locales or Chrome versions. These tests set such fields by
assigning the control's ISO value directly via JavaScript and dispatching
the ``input``/``change`` events the page's own validation and form state
rely on, then re-reading the value to confirm the browser accepted it. This
does not exercise the picker's own keyboard interaction, which is a known,
accepted limitation (see README.md "Limitations").
"""

_SET_VALUE_SCRIPT = """
const element = arguments[0];
const value = arguments[1];
element.value = value;
element.dispatchEvent(new Event('input', {bubbles: true}));
element.dispatchEvent(new Event('change', {bubbles: true}));
"""


def set_value_via_js(driver, element, value):
    """Set ``element.value`` via JavaScript and verify the browser accepted it.

    Used for date/datetime-local inputs (and to reliably clear them) where
    ``send_keys``/``clear`` behavior depends on locale and widget state.
    """
    driver.execute_script(_SET_VALUE_SCRIPT, element, value)
    actual = element.get_attribute("value")
    assert actual == value, (
        f"Expected {element.get_attribute('id')!r} to hold {value!r} after "
        f"assignment, but the browser reports {actual!r}."
    )


def fill_text(element, value):
    """Clear and type into an ordinary text/number/url input or textarea."""
    element.clear()
    if value:
        element.send_keys(value)


def is_natively_invalid(driver, element):
    """True if the browser's own constraint validation would block submission."""
    return not driver.execute_script("return arguments[0].checkValidity();", element)
