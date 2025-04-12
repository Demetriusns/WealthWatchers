<?php
// Process form submission
if($_SERVER['REQUEST_METHOD'] === 'POST') {
    $conn = new mysqli("localhost", "db_user", "db_password", "wealthwatchers");

if($conn->connect_error) {
    die("Connection failed: ". $conn->connect_error);
}

//Collect and sanitize data
$user_id = 1;
$amount = $_POST['amount'];
$category = $_POST['category'];
$description = $_POST['description'];
$date = $_POST['date'];

$stmt = $conn->prepare("INSERT INTO savings (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)");
$stmt->bind_param("idsss", $user_id, $amount, $category, $description, $date);

if ($stmt->execute()) {
    $success = "Savings entry added successfully!";
} else {
    $error = "Error: " . $stmt->error;
}

$stmt->close();
$conn->close();

}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Add Savings Entry</title>
    <link rel="stylesheet" href="WealthWatchersStyle.css">
</head>
<body>
    <div class="container">
        <h2>Add Savings Entry</h2>

        <?php if (!empty($success)) echo "<p class='alert'>$success</p>"; ?>
        <?php if (!empty($error)) echo "<p class='alert'>$error</p>"; ?>

       <form method="POST">
            <label>Amount:</label>
            <input type="number" name="amount" step="0.01" required>

            <label>Category:</label>
            <input type="text" name="category" required>

            <label>Description:</label>
            <textarea name="description"></textarea>

            <label>Date:</label>
            <input type="date" name="date" required>

            <button type="submit">Add Savings</button>
        </form>
    </div>
</body>
</html>
