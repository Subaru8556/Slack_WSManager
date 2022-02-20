$file = (Get-Content -Encoding UTF8 .\tmp.txt) -as [string[]]
$i = 1
foreach ($l in $file){
    if($i -eq 1){
        $hostip = $l
    }elseif($i -eq 2){
        $username = $l
    }elseif($i -eq 3){
        $password = $l
    }
    $i++
}

" " | Out-File -Encoding utf8 .\tmp.txt

#セキュアストリングの生成（パスワードの暗号化）
$sec_str = ConvertTo-SecureString $password -AsPlainText -Force

#Credentialオプションに指定するオブジェクトのインスタンス生成
$psc = New-Object System.Management.Automation.PsCredential($username, $sec_str)

#セッションの生成
$sess = New-PSSession -ComputerName $hostip -Credential $psc

#リモートホスト上でコマンドを実行
#ChromeRDの確認
$chr_stat = Invoke-Command -Session $sess -ScriptBlock {tasklist /fi "imagename eq remoting_desktop.exe"}

#WindowsRDの確認
#$result = @()
$win_stat = Invoke-Command -Session $sess -ScriptBlock {@(query user) -split "\n";}
foreach ($line in $win_stat){
    if($line -match "ユーザー名\sセッション名\sID\s状態\s時間\sログオン時間"){
        #これがヘッダーだった場合配列の次のアイテムに移動する
        continue
    }
    $parsed_server = $line -split "\s+"
    <#
    $result += [PSCustomObject]@{
        server = $parsed_server[0]
        username = $parsed_server[1]
        sessionname = $parsed_server[2]
        id = $parsed_server[3]
        state = $parsed_server[4]
        idle_time = $parsed_server[5]
        logon_time = $parsed_server[6]
    }
    #>
    $session_name = $parsed_server[2]
    $session_state = $parsed_server[4]
}

#セッションを削除
Remove-PSSession -Session $sess

$chrome_state = "error"
$windows_state = "error"

#ChromeRDの利用状況
if($null -ne $chr_stat){
    if("情報: 指定された条件に一致するタスクは実行されていません。" -eq $chr_stat){
        $chrome_state = "chrome notuse"
    }else{
        $chrome_state = "chrome use"
    }
}

#WindowsRDの利用状況
if("Disc" -eq $session_state){
    $windows_state = "windows notuse"
}elseif("Active" -eq $session_state){
    if("console" -eq $session_name){
        $windows_state = "windows use"
    }else{
        $windows_state = "windows remote"
    }
}

#自身のファルダのパスを取得
$path = Split-Path -Parent $MyInvocation.MyCommand.Path

#確認した内容の書き込み
#StreamReaderのコンストラクタに直接「$path + "\test.txt"」を入力するとエラーになるので分けて処理する
$filepath = $path + "\wsstat.txt"
Write-Output $chrome_state | Out-File -FilePath $filepath
Write-Output $windows_state | Out-File -FilePath $filepath -Append