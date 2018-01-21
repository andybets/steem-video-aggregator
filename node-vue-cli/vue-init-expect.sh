#!/usr/bin/expect
set timeout 361
spawn /usr/local/bin/vue init bootstrap-vue/webpack-simple my-project
expect "Project name" { send "\n" }
expect "Project description" { send "\n" }
expect "Author" { send "\n" }
expect "Use sass?" { send "\n" }
interact