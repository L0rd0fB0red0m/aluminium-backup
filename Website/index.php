<!doctype html>
<html>
<?php

  $DB = mysqli_connect("localhost","c2_remymoll","Password not published for security reasons: my own security - Mr. Kientz would kill me","c2_remymoll");
  //Connects to DB whith given Uname PW, and destination

  function load_possible_dests($DB,$language){
    //fetches all possible indexes of table ie. all sub-sites
    $query = mysqli_query($DB,"SELECT name FROM content_$language");
    $response = mysqli_fetch_all($query);
    //returns array of arrays with only one element
    $possible_dests = array();
    foreach ($response as $key => $value) {
      $possible_dests[]=$value[0];
      //creates one array with each available page
    }
    return $possible_dests;
  }

  function load_content($destination,$DB,$language){
    //fetches site content from DB for a given destination
    $query = mysqli_query($DB,"SELECT * FROM content_$language WHERE name = '$destination'");

    $page_content = mysqli_fetch_assoc($query)["content"];
    mysqli_data_seek ($query, 0);
    $page_title = mysqli_fetch_assoc($query)["title"];
    mysqli_data_seek ($query, 0);
    $sidebar_right = mysqli_fetch_assoc($query)["sidebar_right"];
    mysqli_data_seek ($query, 0);
    $sidebar_left = mysqli_fetch_assoc($query)["sidebar_left"];
    $page_all = array(
      "page_title" => $page_title,
      "page_content" => $page_content,
      "sidebar_left" => $sidebar_left,
      "sidebar_right" => $sidebar_right,
    );
    //queries content and title from db and combines them to one array.
    return $page_all;
  };

  function load_links($DB,$language){
    //fetches site content from DB for a given destination
    $query = mysqli_query($DB,"SELECT * FROM content_$language WHERE name = 'links'");

    $links = mysqli_fetch_assoc($query)["content"];
    $links_array = json_decode($links, true);

    return $links_array;
  };

  if(isset($_GET["lang"]) and in_array($_GET["lang"],array("de","fr","en"))){
    $language = $_GET["lang"];
  } else {
    $language = "en";
  }

  $possible_dests = load_possible_dests($DB,$language);#
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

  $page_all = load_content($destination,$DB,$language);
  $links = load_links($DB,$language);
  //loads content to show according to the mentionned criteria

 ?>

<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <meta charset="utf-8">
  <link rel="stylesheet" type="text/css" href="index.css">
  <title>
    Aluminium Backup - <?php echo $page_all["page_title"];?>
  </title>
  <link rel="icon" type="image/aluminium.icon" href="icon.ico">
</head>

<body>
  <div class="menu_bar">
    <a class="logo" href="#"><img id=logo src="icon.ico" alt="logo"></a>
    <div class=title>Aluminium Backup</div>

    <div class="language">
      <a href="#"><?php echo $links["language"]?></a>
      <div class="dropdown-content">
        <a href="?lang=en">English</a>
        <a href="?lang=de">Deutsch</a>
        <a href="?lang=fr">Français</a>
      </div>
    </div>
    <a class="links" href="?dest=contact&lang=<?php echo $language;?>"><?php echo $links["contact"]?></a>
    <a class="links" href="?dest=examples&lang=<?php echo $language;?>"><?php echo $links["examples"]?></a>
    <a class="links" href="?dest=sourcecode&lang=<?php echo $language;?>"><?php echo $links["sourcecode"]?></a>
    <a class="links" href="?dest=downloads&lang=<?php echo $language;?>"><?php echo $links["downloads"]?></a>
    <a class="links" href="?dest=home&lang=<?php echo $language;?>"><?php echo $links["home"]?></a>
    <!--inverse order because shown from right through CSS-->
  </div>

  <br/>

  <div class="main">
    <div class="sidebar_left">
      <?php
        echo $page_all["sidebar_left"];
        //sets page content to the fetched one
      ?>
    </div>
    <div class="website_content">
        <?php
          echo $page_all["page_content"];
          //sets page content to the fetched one
        ?>

    </div>
    <div class="sidebar_right">
      <?php
        echo $page_all["sidebar_right"];
        //sets page content to the fetched one
      ?>
    </div>
  </div>
  
  <div class="footer">
    <a class="logo" href="#"><img id=logo src="icon.ico" alt="logo"></a>
    <div class=title>Aluminium Backup</div>
    <a class="links" href="?dest=info&lang=<?php echo $language;?>"><?php echo $links["info"]?></a>
    <a class="links" href="?dest=legal&lang=<?php echo $language;?>"><?php echo $links["legal"]?></a>
    <a class="links" href="editor.php">Edit</a>
    <!--inverse order because shown from right through CSS-->
  </div>

</body>
</html>
