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
