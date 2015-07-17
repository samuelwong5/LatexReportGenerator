<?php
$f_path = $_REQUEST["file"];
$file = fopen($f_path,"r");
if(!$file) die("[ERROR] File not found.");
$data = array();
$header = fgetcsv($file);
array_push($data, array($header[0], $header[1]));
while(!feof($file))
{
  $temp = fgetcsv($file);
  array_push($data, array($temp[0], (int) $temp[1]));
}
//echo "hello world";
echo json_encode($data);
?>
