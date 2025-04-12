<?php
$conn = new mysqli("localhost", "db_user", "db_password", "wealthwatchers");

if($conn->connect_error) {
    die("Connection failed: ". $conn->connect_error);
}

//Process update
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['update'])) {
    $id = $_POST['id'];
    $amount = $_POST['amount'];
    $category = $_POST['category'];
    $description = $_POST['description'];
    $date = $_POST['date'];

    $stmt = $conn->prepare("UPDATE savings SET amount=?, category=?, description=?, date=?, WHERE id=?");
    $stmt->bind_param("ssssi", $amount, $category, $description, $date, $id);
    $stmt->execute();
    $success = "Savings entry updated.";
}

// Process delete
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['delete'])){
    $id = $_POST['id'];
    $stmt = $conn->prepare("DELETE FROM savings WHERE id=?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $success = "Savings entry deleted.";
}

// Load existing entry
$id = $_GET['id'] ?? null;
$row = null;
if ($id){
    $stmt = $conn->prepare("SELECT * FROM savings WHERE id=?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    $row = $result->fetch_assoc();
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Edit Savings Entry</title>
    <link rel="stylesheet" href="WealthWatchersStyle.css">
</head>
<body>
    <div class="container">
        <h2>Edit Savings Entry</h2>

        <?php if (!empty($success)) echo "<p class='alert'>$success</p>"; ?>
        <?php if (!$row): ?>
            <p class="alert">Savings entry not found.</p>
        <?php else: ?>
            <form method="POST">
                <input type="hidden" name="id" value="<?php echo $row['id']; ?>">

                <label>Amount:</label>
                <input type="number" name="amount" step="0.01" value="<?php echo $row['amount']; ?>" required>

                <label>Category:</label>
                <input type="text" name="category" value="<?php echo $row['category']; ?>" required>

                <label>Description:</label>
                <textarea name="description"><?php echo $row['description']; ?></textarea>

                <label>Date:</label>
                <input type="date" name="date" value="<?php echo $row['date']; ?>" required>

                <button type="submit" name="update">Update</button>
                <button type="submit" name="delete" onclick="return confirm('Are you sure?')">Delete</button>
            </form>
        <?php endif; ?>
    </div>
</body>
</html>
