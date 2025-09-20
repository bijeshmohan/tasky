import os

import httpx
from fasthtml.common import *


API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

app, rt = fast_app(
    title="Tasky",
    hdrs=(
        picolink,
        Script("""
            htmx.on('htmx:responseError', function(evt) {
               alert('Error: ' + evt.detail.xhr.status + ' - ' + evt.detail.xhr.statusText);
            });
        """)
    )
)

client = httpx.AsyncClient(base_url=API_BASE)


def handle(response):
    if response.status_code >= 400:
        error_msg = f"API Error {response.status_code}: {response.text}"
        return Div(
            P(error_msg, style="color: red;"),
            id="error-message"
        )
    return None


def form(item=None, action="/items", method="post"):
    summary = item.get('summary', '') if item else ''
    description = item.get('description', '') if item else ''

    return Form(
        Fieldset(
            Legend("Item Details"),
            Label("Summary:", Input(name="summary", value=summary, required=True)),
            Label("Description:", Textarea(name="description", value=description, rows=3)),
            Button("Save", type="submit"),
            Button("Cancel", type="button", onclick="history.back()")
        ),
        hx_post=action,
        hx_target="#content",
        method=method
    )


def card(item):
    return Article(
        Header(H3(item['summary'])),
        P(item['description']) if item.get('description') else P("No description", style="font-style: italic;"),
        Footer(
            Button(
                "Edit",
                hx_get=f"/items/{item['id']}/edit",
                hx_target="#content",
                style="margin-right: 1rem;"
            ),
            Button(
                "Delete",
                hx_delete=f"/items/{item['id']}/delete",
                hx_target="#content",
                hx_confirm="Are you sure you want to delete this item?"
            ),
            style="display: flex; gap: 1rem; justify-content: flex-start;"
        ),
        style="margin: 1rem 0;"
    )


@rt("/")
async def index():
    try:
        response = await client.get(f"/items")
        response.raise_for_status()
        items = [card(item) for item in response.json()] if response.json() else [P("No items found.")]
        content = Div(
            Div(
                Button("New", hx_get="/items/new", hx_target="#content"),
                style="margin-bottom: 2rem;"
            ),
            Div(*items),
            id="items-list"
        )
    except httpx.HTTPError as e:
        content = Div(
            P(f"Error connecting to API: {str(e)}", style="color: red")
        )

    return Titled(
        "Tasky",
        Main(
            Div(content, id="content"),
            Container=True
        )
    )


@rt("/items/new")
async def new():
    return Div(
        H2("Create New Item"),
        form(action="/items/create"),
        Button(
            "Back",
            hx_get="/",
            hx_target="#content",
        ),
        id="create-form"
    )


@rt("/items/create")
async def create(summary: str, description: str = ""):
    try:
        data = {"summary": summary, "description": description}
        response = await client.post(f"/items", json=data)
        error = handle(response)
        if error:
            return error

        return Div(
            P("Item created successfully.", style="color: green;"),
            Script("setTimeout(() => { htmx.ajax('GET', '/', {target: '#content'}); }, 1500);")
        )
    except httpx.HTTPError as e:
        return Div(
            P(f"Error creating item: {str(e)}", style="color: red"),
            Button("Try Again", onClick="history.back()")
        )


@rt("/items/{id}/edit")
async def edit(id: str):
    try:
        response = await client.get(f"/items/{id}")
        error = handle(response)
        if error:
            return error

        item = response.json()
        return Div(
            H2(f"Edit Item: {item['summary']}"),
            form(item=item, action=f"/items/{id}/update", method="put"),
            Button("Back",
                   hx_get="/",
                   hx_target="#content"),
            id="edit-form"
        )
    except httpx.HTTPError as e:
        return Div(
            P(f"Error loading item: {str(e)}", style="color: red;"),
            Button("Back", hx_get="/", hx_target="#content")
        )


@rt("/items/{id}/update")
async def update(id: str, summary: str, description: str = ""):
    try:
        data = {"summary": summary, "description": description}
        response = await client.patch(f"/items/{id}", json=data)
        error = handle(response)
        if error:
            return error

        return Div(
            P("Item updated successfully.", style="color: green;"),
            Script("setTimeout(() => { htmx.ajax('GET', '/', {target: '#content'}); }, 1500);")
        )
    except httpx.HTTPError as e:
        return Div(
            P(f"Error updating item: {str(e)}", style="color: red;"),
            Button("Try Again", onClick="history.back()")
        )


@rt("/items/{id}/delete")
async def delete(id: str):
    try:
        response = await client.delete(f"/items/{id}")
        error = handle(response)
        if error:
            return error

        return Div(
            P("Item deleted successfully.", style="color: green;"),
            Script("setTimeout(() => { htmx.ajax('GET', '/', {target: '#content'}); }, 1500);")
        )
    except httpx.HTTPError as e:
        return Div(
            P(f"Error deleting item: {str(e)}", style="color: red;"),
            Button("Back", hx_get="/", hx_target="#content")
        )


if __name__ == "__main__":
    serve()
