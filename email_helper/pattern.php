<!DOCTYPE html>

<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1" name="viewport"/>
    <meta content="" name="description"/>
    <title>LinuxNetwork 2022 progress check site</title>
    <link href="https://uneex.ru/favicon.ico" rel="shortcut icon"/>
    <!--Frameworks-->
    <link href="https://timetable.veniamin.space/css/bootstrap.css" rel="stylesheet"/>
    <script crossorigin="anonymous" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM"
            src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <!--General ccs, js-->
    <link href="https://timetable.veniamin.space/css/night_mode.css" rel="stylesheet"/>
    <script src="https://timetable.veniamin.space/js/night_mode.js"></script>
    <style>
        html {
            height: 100vh;
        }

        body {
            min-height: 100vh;
            max-height: 100vh;
            max-width: 100vw;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-bottom: 5rem;
        }

        .form-control-general {
            max-width: 90%;
            margin: auto;
        }

        @media screen and (max-width: 800px) {
            .form-control-general {
                max-width: 100%;
                margin: auto;
            }

            tbody tr th:first-child {
                max-width: 40vw;
                overflow: hidden;
            }
        }

        .bg-purple {
            background-color: #7B68EE !important;
        }

        .night-mode .bg-success {
            filter: invert(100%);
        }

        .night-mode  .bg-purple {
            filter: invert(100%);
        }

        .night-mode .bg-warning {
            filter: invert(100%);
        }

        .night-mode .bg-danger {
            filter: invert(100%);
        }

        .night-mode .bg-primary {
            filter: invert(100%);
        }

        .night-mode .bg-info {
            filter: invert(100%);
        }

        thead tr:first-child th {
            position: sticky;
            top: 0;
            background: #FFFFFF;
            z-index: 1;
        }

        tbody tr th:first-child {
            position: sticky;
            left: 0;
            background: #FFFFFF;
            z-index: 1;
        }

        .my_fit {
            height: 80vh;
        !important;
        }
    </style>
</head>
<body class="">
<div class="text-center form-control-general">
    <?php
    $is_admin = isset($_COOKIE["super_secret_cookie"]) && $_COOKIE["super_secret_cookie"] === "LinuxNetwork2022";
    ?>
    <h1 class="h3 mb-3 fw-normal">LinuxNetwork2022 Progress Check</h1>
    <div class="row justify-content-center">
        <div class="col">
            <textarea id="cookie_textarea" placeholder="Type your cookie here"></textarea>
        </div>
        <div class="col"><text class="p-2 bg-success">Passed on time</text></div>
        <div class="col"><text class="p-2 bg-warning">Overdue for a week</text></div>
        <div class="col"><text class="p-2 bg-danger">Overdue more than a week</text></div>
        <div class="col"><text class="p-2 bg-primary">Plagiarism</text></div>
        <div class="col"><text class="p-2 bg-info">Bag archive</text></div>
        <div class="col">
            <button class="btn bg-purple" id="cookie-button" type="button">Set cookie</button>
            <script>
                $(function () {
                    let cookie_textarea = $("#cookie_textarea");
                    let cookie_button = $("#cookie-button");

                    cookie_button.on("click", function (e) {
                        document.cookie = "super_secret_cookie=" + cookie_textarea.val() + ";";
                        window.location.reload();
                    });
                });
            </script>
        </div>
    </div>
    <div class="overflow-scroll my_fit">
        <table class="table table-hover table-striped table-bordered align-middle" id="main_table">
        </table>
    </div>
    <?php
    if ($is_admin) {
        echo
        '
    <form action="data.php" method="POST" target="_blank" id="data_form" hidden>
<input id="form_username" name="username" type="text"/>
<input id="form_homework_name" name="homework_name" type="text"/>
<input name="form_submit" type="submit"/>

<script>
        $(function () {
            $("tbody > tr > th").on("click", function (e) {
                let username = $(e.currentTarget).parent().children()[0].innerText.replace("&nbsp;", " ")
                let col_index = $(e.currentTarget).index($(e.currentTarget).innerText);
                if (col_index > 1) {
                    $("#form_username").val(username);
                    $("#form_homework_name").val($("thead > tr > th")[col_index].innerText);
                    $("#data_form").trigger("submit");
                    console.log($("thead > tr > th")[col_index].innerText);
                    console.log(username);
                }
            });
        });
    </script>
';
    }
    ?>

    <h6 id="update-time">Last updated: 12 Jun 08:50</h6>
</div>
<footer class="bg-transparent fixed-bottom-right">
    <div class="container-fluid">
        <a class="btn btn-danger btn-lg night-button m-2 fs-6">Night Mode</a>
    </div>
</footer>
</body>
</html>
