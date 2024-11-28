// delete js function

function confirmDelete(event, name) {
    const confirmed = confirm(`Do you want to delete ${name}? This cannot be undone.`);
    if (!confirmed) event.preventDefault();
}

// Display More Rows
function loadMore() {
    document.querySelectorAll('.hidden').forEach(row => row.classList.remove('hidden'));
    document.getElementById('loadMoreClients').style.display = 'none';
    document.getElementById('showLessClients').style.display = 'inline';
}

// Display Less Rows
function showLess() {
    document.querySelectorAll('tr').forEach((row, index) => {
        if (index > 3) {
            row.classList.add('hidden');
        }
    });
    document.getElementById('loadMoreClients').style.display = 'inline';
    document.getElementById('showLessClients').style.display = 'none';
    
}