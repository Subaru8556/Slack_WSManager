# Slack_WSManager<br>
Slack上でパソコンのリモートアクセスの利用状況を確認するbotです<br>
Windows上で動作させることを想定して作成してあります<br>
<br>

# 動作させるために<br>
Slack Appに関する操作はクライアント(このbotを動作させるためのコンピューター)側で行うことを想定している<br>

## Slack Appの作成<br>
まだAppを作成していない場合、[このリンク](https://api.slack.com/apps)から新たにAppを作成する<br>
作成する際は、`Create an app` は From scratchを選択し、`App name` は好きな名前を、`Pick a workspace to develop your app in:` にこのbotを使いたいワークスペースを選択する。
<br>
## Slack Appの設定<br>
`Settings -> Socket Mode`<br>
Socket Mode を有効化する<br>
この際作成するトークンは後で SLACK_APP_TOKEN として利用する<br>
<br>
`Features -> Event Subscriptions`<br>
Event を有効化する<br>
Subscribe to bot events に以下のイベントを追加する<br>

    message.channels
    message.groups
    message.im
    message.mpim
<br>

`Features -> OAuth & Premissions`<br>
Scopes の Bot Token Scopes に以下のスコープが追加されているのを確認する<br>

    channels:history
    groups.history
    im:history
    mpim:history
<br>

`Features -> App Home`<br>
Always Show Bot as Online を有効化する<br>
Show Tabs の Messages Tab を有効化する<br>
<br>

## Slack Appのインストール<br>
`Settings -> Basic Information`<br>
Install your app からワークスペースにインストールする<br>
<br>

## Slack AppのTokenの確認<br>
`Settings -> Basic Information`<br>
App-Level TokensにSocket Modeを有効化する際に作成したTokenがあるので、それを `SLACK_APP_TOKEN` としてbotを動作させるシステム環境変数に追加する<br>
<br>

`Features -> OAuth & Premissions`<br>
OAuth Tokens for Your Workspace の Bot User OAuth Token を `SLACK_BOT_TOKEN` としてシステム環境変数に追加する<br>
※Bot User OAuth Token はAppをインストールしてからでないと生成されないので、必ず先にワークスペースにインストールしてからTokenを確認する<br>
<br>

## 暗号・複合化の準備<br>
暗号・複合化に関しては、[このリンク](https://github.com/senkousya/usingEncryptedStandardStringOnPowershell)先の内容を参考にしています<br>
<br>
暗号・複合化の部分のコードは既に書いてあるので、ここでは暗号・複合化に必要な鍵の生成を行います<br>
<br>
PowerShellにて以下のコードを実行してください

    $EncryptedKey = New-Object Byte[] 24

    [Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($EncryptedKey)

    $EncryptedKey

すべて実行すると、24個の数字が<br>

    aaa
    bbb
    ccc
     ︙

という感じに表示されるので、この数字を<br>

    aaa,bbb,ccc,…

のようにして、システム環境変数に `SLACK_BOT_CRYPTO` として追加する<br>
<br>

## PSSessionを利用できるようにする<br>
このbotではリモートアクセスの利用状況を確認するために、リモートコンピューターとのPowerShellセッション(PSSession)を作成しているため、このbotの利用前にリモートコンピューターへ接続できるようにしておく<br>
<br>

## サーバー(アクセス先)側の操作<br>
このbotで利用状況を確認する対象のコンピューターで以下の操作を行う

## PSRemotingの有効化<br>
PowerShellで以下のコードを実行する<br>

    Get-NetConnectionProfile

すると、以下のような出力が得られる<br>
※これは、こちらの環境で実行した結果を元に作成しているため実行した環境によって出力の結果は異なる<br>

    Name             : Ethernet名
    InterfaceAlias   : イーサネット 2
    InterfaceIndex   : 13
    NetworkCategory  : Private
    IPv4Connectivity : Internet
    IPv6Connectivity : NoTraffic

    Name             : ネットワーク 2
    InterfaceAlias   : Tailscale
    InterfaceIndex   : 5
    NetworkCategory  : Private
    IPv4Connectivity : LocalNetwork
    IPv6Connectivity : NoTraffic

    Name             : 識別されていないネットワーク
    InterfaceAlias   : VMware Network Adapter VMnet1
    InterfaceIndex   : 7
    NetworkCategory  : Public
    IPv4Connectivity : LocalNetwork
    IPv6Connectivity : NoTraffic

この中に `NetworkCategory` が Public のものがあるとこの後の処理を行うことができないため、もしそのようなネットワークがあった場合は管理者として実行したPowerShellで以下のコードを実行する

    Get-NetConnectionProfile -Name "network name" | Set-NetConnectionProfile -NetworkCategory private

例として、上記の私の環境でこの操作を行う場合次のようなコードを実行すればよい

    Get-NetConnectionProfile -Name "識別されていないネットワーク" | Set-NetConnectionProfile -NetworkCategory private

`NetworkCategory` がPublicであるネットワークがなくなったら、管理者として実行したPowerShellで以下のコードを実行する

    Enable-PSRemoting

この操作が成功したら、サーバー側での操作は終了<br>
<br>

## クライアント(アクセス元)側の操作<br>
このbotを動作させるコンピューターで以下の操作を行う<br>
<br>

## WinRMの起動
WinRMというPowerShellを遠隔から操作する機能を起動するために、管理者として実行したPowerShellで以下のコードを実行する<br>

    net start WinRM

## WinRMのTrastedHostsにサーバー側のコンピューターを追加する
WinRMでサーバーに接続するために、サーバーを信頼済みホストとして登録する必要があるため管理者として実行したPowerShellで以下のコードを実行する

    Set-Item WSMan:\localhost\Client\TrustedHosts -Value (ホスト名またはIPアドレス)

推奨はしないが、以下のコードを実行すると、すべてのホストを信頼することができる

    Set-Item WSMan:\localhost\Client\TrustedHosts -Value *

もし、アクセス先のコンピューターが同一ネットワーク内になく、パブリックIPもない場合[TailScale](https://tailscale.com/)などのVPNサービスを利用しても問題なくこのbotは使用することができる<br>
その場合、TrastedHostsのIPアドレスにはTailScaleで割り当てられるIPアドレスを入力する<br>
<br>

TailScaleを利用する場合、TailScaleをサーバー側とクライアント側の両方にインストールして同じアカウントでログインする必要がある<br>
また、TailScaleでは初期設定で6か月でTailScale内のキーの有効期限が切れ、接続ができなくなってしまうため以下の設定をしてキーの有効期限を無効化しておいた方がよい<br>
<br>
[このリンク](https://tailscale.com/)からTailScaleにログインし、Machinesを開く<br>
有効期限の無効化を行いたいコンピューター名の横の `…` をクリックして `Disable key expiry` を選択する<br>
<br>

以上でクライアント側の操作も終了<br>
<br>


# 動作させる前に
これまでの準備でリモートコンピューターにアクセスする準備は出来たが肝心のアクセスに必要な情報が用意できていないためそれを用意していく<br>
<br>


## 不要なファイルの削除
GitHubにWorkStationsフォルダをアップロードするために、フォルダの中に `delete_this_file.txt` というなんの意味もないファイルがあるのでこれを削除する<br>
このファイルが残っているとbotの動作に影響を与える可能性があるので必ず消すこと<br>
<br>


## tmp.txtに書き込み
tmp.txtに以下のフォーマットでサーバーの情報を書き込む<br>

    1行目:サーバーの表示名(コマンドでサーバーを指定する際に使う名前なので、短く分かりやすいものが好ましい)
    2行目:サーバー名・サーバーIP
    3行目:リモートアクセスする際のユーザー名
    4行目:リモートアクセスする際のパスワード
    5行目:Chrome リモートデスクトップのPIN(任意)(passコマンドで表示させる内容)
    6行目:Windows のPIN(任意)(passコマンドで表示させる内容)
    7行目:Windows のパスワード(任意)(passコマンドで表示させる内容)

もし、`Host-Computer` というパソコンに `User` , `1234` というユーザー名、パスワードでログインでき,<br>
ChromeリモートデスクトップのPINが `123456` 、WindowsのPINとパスワードがそれぞれ、 `1111` ,  `password` とするとtmp.txtに書き込む内容は以下のようになる<br>

    host
    Host-Computer
    User
    1234
    123456
    1111
    password

tmp.txtに書き込み終わったらtmp.txtを保存し、 `crypto.ps1` を実行する<br>
成功すれば、WorkStationsフォルダに `サーバーの表示名.txt` というファイルが生成されその中に暗号化された文章が書いてある<br>
この例の場合だと `host.txt` というファイルが生成される<br>
<br>

もし、`crypto.ps1` が実行できない場合、Readme.mdの下の方に記述してある `PowerShellスクリプトが実行できない場合` を参考に操作を行う<br>
この操作を追加したいコンピューターの分行う<br>
一度に一台分の情報しか暗号化できないため、コンピューターの数だけ繰り返す必要がある<br>
<br>

# Appを起動する<br>
app.pyを実行する<br>
コンソールに `Bolt app is running!` と表示されれば起動は成功している<br>
起動が失敗した場合は、Tokenが間違っていないか、システム環境変数の名前が間違えていないかなど確認する<br>

また、app.pyをVisual Studio Codeなどのエディターから起動すればエラーのより詳細な情報を得ることができる<br>

起動したら、botのいるチャンネルまたは、ダイレクトメッセージで `help` と送信するか、以下に書くコマンドの一覧を参考に利用する<br>
<br>

# コマンド一覧<br>
(WS = WorkStation)<br>

**stat**<br>
WSのリモートアクセスの利用状況を調べます<br>
stat のみで実行するとすべてのWSの利用状況を調べます<br>
WS名をつけることで、指定したWSの利用状況を調べることもできます<br>
例）

    stat
    stat host
<br>

**use**<br>
WSの利用開始を記録します<br>
use のみで実行するとすべてのWSに対して利用開始を記録します<br>
WS名をつけることで、指定したWSに対して利用開始を記録することもできます<br>
WSを複数人数で共有している場合など、誰が使っているか把握できた方が便利な場合に使ってください<br>
例）

    use
    use host
<br>

**end**<br>
WSの利用終了を記録します<br>
end のみで実行するとすべてのWSに対して利用終了を記録します<br>
WS名をつけることで、指定したWSに対して利用終了を記録することもできます<br>
WSを複数人数で共有している場合など、誰が使っているか把握できた方が便利な場合に使ってください<br>
例）

    end
    end host
<br>

**pass**<br>
WSへの各種アクセスに必要な情報を表示します<br>
pass のみで実行するとすべてのWSへの各種アクセスに必要な情報を表示します<br>
WS名をつけることで、指定したWSへの各種アクセスに必要な情報を表示することもできます<br>
例）

    pass
    pass host
<br>

**opendm**<br>
WSManagerとのDMを開始します<br>
誤ってDMを閉じてしまった際などに利用してください<br>
例）

    opendm
<br>

**help**
上記の内容とほぼ同じ文章をSlack上で送信します<br>
コマンドを忘れてしまった場合などに利用してください<br>
例）

    help
<br>

# PowerShellスクリプトが実行できない場合<br>

## ExecutionPolicyの確認<br>
もし、PowerShellスクリプトが実行できない場合、PowerShellで以下のコードを実行する<br>

    Get-ExecutionPolicy

その結果が `Restricted` の場合、すべてのスクリプトの実行が制限されているため、以下の操作のどちらかを行う<br>
<br>

## ExecutionPolicyの変更<br>
1.ExecutionPolicyによる実行ポリシーの変更<br>
PowerShellを開き、ダウンロードしたSlack_WSManagerのディレクトリに移動する<br>
スクリプトを実行する際に、PowerShellで以下のようなコードを実行する(xxxは実行するスクリプト名)

    PowerShell -ExecutionPolicy RemoteSigned .\xxx.ps1
<br>

2.Set-ExecutionPolicyによる実行ポリシーの変更(恒久的)<br>
管理者として実行したPowerShellで以下のコードを実行する

    Set-ExecutionPolicy RemoteSigned

ExecutionPolicyの `RemoteSigned` とはローカル上のスクリプトとそれ以外の署名付きスクリプトを実行するようにするポリシーのこと<br>
<br>

このどちらかを行ってもまだ実行できない場合次の操作を行う<br>
<br>

## Zoneidの削除
Powershellを開き、ダウンロードしたSlacl＿WSManagerのディレクトリに移動して、次のコードを実行する

    Get-ChildItem -Recurse -File | ?{$_ | Get-Item -Stream Zone.Identifier -ErrorAction Ignore;} | Remove-Item -Stream Zone.Identifier;

このコードを実行すると、このコードを実行したディレクトリ以下のフォルダに対してZoneidの削除を行う<br>
そうすることで、インターネットからダウンロードしたファイルではなくローカル上のスクリプトとして実行されるため、実行する際に署名を求められることはないはず…<br>

この状態で、先ほど.1を実行した場合はもう一度.1を、.2を実行した場合は好きな方法でスクリプトの実行を試みる<br>
もしそれでも、署名を求められた際は次の操作を行う<br>
<br>

## 証明書の作成<br>
[このサイト](https://fnya.cocolog-nifty.com/blog/2017/01/powershell-6c78.html)を参考にしています<br>
<br>
まず、Visual Studioがインストールされていない場合[ここ](https://visualstudio.microsoft.com)からインストールする<br>
<br>

## ローカル認証局を作成<br>
Developer Command Prompt for VSxxxx(インストールしたVisual Studioのバージョンによって違う)<br>
インストールしたのが Visual Studio 2022 なら `Developer Command Prompt for VS2022` になる<br>
<br>
開いたら以下のコマンドを実行する<br>

    makecert -n "CN=PowerShell Local Root" -a sha256 -eku 1.3.6.1.5.5.7.3.3 -r -sv root.pvk root.cer -ss Root -sr localMachine

このコマンドで `PowerShell Local Root` というローカル認証局を作成する<br>

また、このコマンドを実行した際にパスワードを要求されるが、何も入力せずにOKを選ぶ<br>
そうすると、確認のメッセージが表示されるため、はいを選ぶ<br>
<br>

## 証明書を作成<br>
Developer Command Prompt for VSxxxxを開き、以下のコマンドを実行する

    makecert -pe -n "CN=PowerShell User" -ss MY -a sha256 -eku 1.3.6.1.5.5.7.3.3 -iv root.pvk -ic root.cer
<br>

## スクリプトに署名する<br>
PowerShellで以下のコードを実行する

    $FilePath = 署名したいスクリプトのパス
    $Cn = "PowerShell User"
    $Cert = Get-ChildItem Cert:\CurrentUser\My | ? {$_.Subject -eq "CN=$Cn"}
    Set-AuthenticodeSignature -Cert $Cert -Filepath $FilePath

このコードを実行した後に表示される `Status` が Valid であれば署名は成功している<br>
<br>

## 署名後に気をつけること<br>
署名後にスクリプトの内容を変更すると実行するためには再署名が必要になる
