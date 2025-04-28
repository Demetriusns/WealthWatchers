function markAsRead(notification_id) {
        fetch(`/mark_as_read/${notification_id}`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            // Update the unread notification count in the navbar
            document.getElementById('unread-count').textContent = data.unread_count;

            // Optionally, hide or mark the notification as read on the page
            const notificationElement = document.getElementById(`notification-${notification_id}`);
            notificationElement.classList.remove('unread');
            notificationElement.querySelector('.mark-read-btn').style.display = 'none';
        })
        .catch(error => console.error('Error:', error));
    }
