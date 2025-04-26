console.log('category_manage.js loaded');

function showToast(message, isDelete = false) {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast';

    if (isDelete) {
        toast.style.backgroundColor = '#ffe5e5';
        toast.style.border = '1px solid #ff4d4d';
        toast.style.color = '#a80000';
    }

    toast.textContent = message;
    toastContainer.appendChild(toast);

    void toast.offsetHeight;

    setTimeout(() => {
        toast.remove();
    }, 2000);
}

function handleDeleteForm(e) {
    e.preventDefault();

    const form = this;
    const categoryId = form.getAttribute('data-category-id');

    fetch(`/delete_category/${categoryId}`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const row = form.closest('tr');
            row.remove();
            showToast(`Category "${data.category_name}" deleted from list.`, true);
        }
    })
    .catch(error => console.error('Delete error:', error));
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.delete-category-form').forEach(form => {
        form.addEventListener('submit', handleDeleteForm);
    });

    document.getElementById('add-category-form').addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);

        fetch('/categories', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const tableBody = document.querySelector('tbody');
                const newRow = document.createElement('tr');

                newRow.innerHTML = `
                    <td>${data.category.category_name}</td>
                    <td>${data.category.description}</td>
                    <td>
                        <form data-category-id="${data.category.category_id}" class="delete-category-form" method="POST" style="display:inline;">
                            <button class="btn" type="submit">Delete</button>
                        </form>
                    </td>
                `;

                tableBody.appendChild(newRow);

                newRow.querySelector('.delete-category-form').addEventListener('submit', handleDeleteForm);

                showToast(`Category "${data.category.category_name}" added to list.`);
                document.getElementById('add-category-form').reset();
            }
        })
        .catch(error => console.error('Error:', error));
    });
});
