$key = $env:SLACK_BOT_CRYPTO
$array = $key.Split(",")
[byte[]] $EncryptedKey = ($array[0],$array[1],$array[2],$array[3],$array[4],$array[5],$array[6],$array[7],$array[8],$array[9],$array[10],$array[11],$array[12],$array[13],$array[14],$array[15],$array[16],$array[17],$array[18],$array[19],$array[20],$array[21],$array[22],$array[23])

$SecureString = Get-Content .\tmp.txt | ConvertTo-SecureString -key $EncryptedKey

$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureString)

$StringPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)

$StringPassword | Out-File -Encoding utf8 .\tmp.txt