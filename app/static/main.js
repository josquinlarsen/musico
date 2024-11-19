// delete js function

function confirmDelete(event, name) {
    const confirmed = confirm(`Do you want to delete ${name}? This cannot be undone.`);
    if (!confirmed) event.preventDefault();
}