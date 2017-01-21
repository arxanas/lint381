" lint381.vim --- style check your code according to EECS 381 style guidelines

" This file depends on cpp/lint381.vim -- see cpp/lint381.vim

if exists('g:loaded_syntastic_c_lint381_checker')
  finish
endif
let g:loaded_syntastic_c_lint381_checker = 1

call g:SyntasticRegistry.CreateAndRegisterChecker({
  \ 'filetype': 'c',
  \ 'name': 'lint381',
  \ 'redirect': 'cpp/lint381'})
