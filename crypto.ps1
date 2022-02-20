$key = $env:SLACK_BOT_CRYPTO
$array = $key.Split(",")
[byte[]] $EncryptedKey = ($array[0],$array[1],$array[2],$array[3],$array[4],$array[5],$array[6],$array[7],$array[8],$array[9],$array[10],$array[11],$array[12],$array[13],$array[14],$array[15],$array[16],$array[17],$array[18],$array[19],$array[20],$array[21],$array[22],$array[23])

$file = (Get-Content .\tmp.txt) -as [string[]]

$i = 1
foreach ($l in $file) {
    if($l.Contains("$")){
        $l = $l.Replace("$","`$")
    }
    if($i -eq 1){
        $WSName = $l
    }elseif($i -eq 2){
        $hostip = $l
    }elseif($i -eq 3){
        $username = $l
    }elseif($i -eq 4){
        $password = $l
    }elseif($i -eq 5){
        $chrome_pin = $l
    }elseif($i -eq 6){
        $ws_pin = $l
    }elseif($i -eq 7){
        $ws_pass = $l
    }
    $i++
}

$newline = "`r`n"

$string = $hostip + $newline + $username + $newline + $password + $newline + $chrome_pin + $newline + $ws_pin + $newline +$ws_pass

$SecureString = ConvertTo-SecureString -String "$string" -AsPlainText -Force

$Encrypted = ConvertFrom-SecureString -SecureString $SecureString -Key $EncryptedKey

$Encrypted | Out-File .\WorkStations\$WSName.txt