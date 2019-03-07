<!doctype html>

<html>

<?php
  $DB = mysqli_connect("localhost","u155424db1","***REMOVED***","u155424db1");
  //Connects to DB whith given Uname PW, and destination

  function load_possible_dests($DB){
    //fetches all possible indexes of table ie. all sub-sites
    $query = mysqli_query($DB,"SELECT name FROM ws_content");
    $response = mysqli_fetch_all($query);
    //returns array of arrays with only one element
    $possible_dests = array();
    foreach ($response as $key => $value) {
      $possible_dests[]=$value[0];
      //creates one array with each available site
    }
    return $possible_dests;
  }

  function load_content($destination,$DB){
    //fetches site content from DB for a given destination
    $query = mysqli_query($DB,"SELECT * FROM ws_content WHERE name = '$destination'");
    $page_content = mysqli_fetch_assoc($query)["content"];
    $query = mysqli_query($DB,"SELECT * FROM ws_content WHERE name = '$destination'");
    $page_title = mysqli_fetch_assoc($query)["title"];
    $page_all = array($page_title,$page_content);
    //queries content and title from db and combines them to one array. calls query twice bc. fetch_assoc apparently empties $query
    return $page_all;
  };

  $possible_dests = load_possible_dests($DB);#
  //if no argument is given throuh the URL: shows home (ie. start page)
  //if argument does not match any existing site in DB: shows 404
  if(isset($_GET['dest'])){
    if(in_array($_GET['dest'],$possible_dests)){
      $destination = $_GET['dest'];
    } else {
      $destination = 'e404';
    };
  } else {
    $destination = "home";
  };

  $page_all = load_content($destination,$DB);
  //loads content to show according to the mentionned criteria
 ?>


<head>
  <meta charset="utf-8">
  <link rel="stylesheet" type="text/css" href="index.css">
  <title>
    Aluminium Backup - <?php echo $page_all[0];
    //sets page title to the fetched one
    ?>
  </title>
</head>

<body>
  <div class="menu_bar">
    <div class=logo><img src="icon.ico" alt="logo"></div>
    <div class=title>Aluminium Backup</div>
    <a href="?dest=contact">Contact</a>
    <a href="?dest=examples">Examples</a>
    <a href="?dest=sourcecode">Source-Code</a>
    <a href="?dest=versions">Versions</a>
    <a href="?dest=downloads">Downloads</a>
    <a href="?dest=home">Home</a>
    <!--inverse order because shown from right through CSS-->
  </div><br/>
  <div class="main">
      <?php
        echo utf8_decode($page_all[1]);
        //sets page content to the fetched one
      ?>
  </div><br/>
  <div class="footer">
    <div class=logo><img src="icon.ico" alt="logo"></div>
    <div class=title>Aluminium Backup</div>
    <a href="?dest=info">Info</a>
    <a href="?dest=legal">Legal</a>
    <a href="/editor.php">Edit</a>
    <!--inverse order because shown from right through CSS-->
  </div>

</body>
</html>
