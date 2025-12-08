document.addEventListener("DOMContentLoaded", function () {
    const addBtn = document.getElementById("add");
    const removeBtn = document.getElementById("remove");
    const table = document.querySelector(".user-table");

    // counter starts at 1
    let counter = 1;

    function createRow(index) {
        const row = table.insertRow(-1);

        // Start Time
        const cell1 = row.insertCell(0);
        const startInput = document.createElement("input");
        startInput.type = "time";
        startInput.name = `shift-${index}-start`;
        cell1.appendChild(startInput);

        // End Time
        const cell2 = row.insertCell(1);
        const endInput = document.createElement("input");
        endInput.type = "time";
        endInput.name = `shift-${index}-end`;
        cell2.appendChild(endInput);

        // Number of People
        const cell3 = row.insertCell(2);
        const numInput = document.createElement("input");
        numInput.type = "number";
        numInput.min = "1";
        numInput.value = "1";
        numInput.name = `shift-${index}-count`;
        cell3.appendChild(numInput);
    }

    addBtn.addEventListener("click", function () {
        createRow(counter);
        counter++;
    });

    removeBtn.addEventListener("click", function () {
        // only remove if there is at least one data row
        if (table.rows.length > 1) { // keep header
            table.deleteRow(-1);
            counter--;
        }
    });

    // optional: add one row by default
    createRow(counter);
    counter++;
});
