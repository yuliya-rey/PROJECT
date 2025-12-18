document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.task-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskId = this.dataset.taskId;
            const completed = this.checked;
            updateTaskStatus(taskId, completed);
        });
    });

    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.dataset.taskId;
            deleteTask(taskId);
        });
    });
});

async function updateTaskStatus(taskId, completed) {
    try {
        const response = await fetch(`/tasks/${taskId}?completed=${completed}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            setTimeout(() => {
                location.reload();
            }, 500);
        } else {
            alert('Ошибка при обновлении задачи');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка при обновлении задачи');
    }
}

async function deleteTask(taskId) {
    if (confirm('Вы уверены, что хотите удалить эту задачу?')) {
        try {
            const response = await fetch(`/tasks/${taskId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                location.reload();
            } else {
                alert('Ошибка при удалении задачи');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Ошибка при удалении задачи');
        }
    }
}
