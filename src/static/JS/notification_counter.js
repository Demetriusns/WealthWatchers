function markAsRead(notification_id) {
        fetch(`/mark_as_read/${notification_id}`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {

          const unreadCountSpan = document.getElementById('unread-count');
          unreadCountSpan.textContent = data.unread_count;

          if (data.unread_count > 0) {
            unreadCountSpan.classList.add('active');
          } else {
            unreadCountSpan.classList.remove('active');
          }

            // Optionally, hide or mark the notification as read on the page
            const notificationElement = document.getElementById(`notification-${notification_id}`);
            notificationElement.classList.remove('unread');
            notificationElement.querySelector('.mark-read-btn').style.display = 'none';
        })
        .catch(error => console.error('Error:', error));
    }

function deleteNotification(notification_id) {
      fetch(`/delete_notification/${notification_id}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const notificationElement = document.getElementById(`notification-${notification_id}`);
                notificationElement.remove();

                const unreadCountSpan = document.getElementById('unread-count');
                unreadCountSpan.textContent = data.unread_count;

                if (data.unread_count > 0) {
                    unreadCountSpan.classList.add('active');
                } else {
                    unreadCountSpan.classList.remove('active');
                }
            } else {
                console.error('Failed to delete notification:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }
