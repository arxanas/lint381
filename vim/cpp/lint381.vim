" lint381.vim --- style check your code according to EECS 381 style guidelines

" This checker filters your code through the lint381 application and displays
" the violations of the EECS 381 style guide right within your vim editor.
" It requires that the lint381 program lives in your path, and that you have
" the Syntastic plugin for vim installed.

" The lint381 program: https://github.com/arxanas/lint381
" See also the EECS 381 style guides:
  " http://www.umich.edu/~eecs381/handouts/C_Coding_Standards.pdf
  " http://www.umich.edu/~eecs381/handouts/C++_Coding_Standards.pdf

" To use this:
  " 1) Ensure that you have Syntastic installed: https://github.com/vim-syntastic/syntastic
  " 2) Place this file in ~/.vim/bundle/syntastic/syntax_checkers/cpp
  " 3) Place the c/lint381.vim file in ~/.vim/bundle/syntastic/syntax_checkers/c
  " 4) Add these lines to your vimrc: 
    " let g:syntastic_cpp_checkers = ['lint381']
    " let g:syntastic_c_checkers = ['lint381']
    " Of course, precede 'lint381' with any other linters you may wish to use, e.g.:
      " let g:syntastic_cpp_checkers = ['cppcheck', 'lint381']

  " Note that if you have multiple checkers enabled, the defualt behavior of Syntastic
  " is to run them in sequence, continuing with the next checker ONLY once the previous
  " checker returns no errors. 
  " To tell Syntastic to always run all checkers, add this to your vimrc:
    " let g:syntastic_aggregate_errors = 1

if exists('g:loaded_syntastic_cpp_lint381_checker')
  finish
endif
let g:loaded_syntastic_cpp_lint381_checker = 1

if !exists('g:syntastic_cpp_lint381_sort')
  let g:syntastic_cpp_lint381_sort = 1
endif

let s:save_cpo = &cpo
set cpo&vim

" Since lint381 only prints the basename of the file being edited,
" if the user edits a file that is not in the current working directory,
" syntastic ends up telling vim that the identified errors are in a file
" in the cwd with the printed name. 
" To fix this, we convert the basenames to absolute paths.
function! Basenames_to_absolute_paths(errors) abort
    let out = []
    for err in a:errors
        let str = expand('%:h') . '/' . err
        echom str
        call add(out, str)
    endfor
  return out 
endfunction

let s:default_args = {
  \ 'c': '--lang=c',
  \ 'cpp': '--lang=cpp'}

function! SyntaxCheckers_cpp_lint381_IsAvailable() dict
  return executable(self.getExec())
endfunction

function! SyntaxCheckers_cpp_lint381_GetLocList() dict
  let makeprg = self.makeprgBuild({'args': get(s:default_args, self.getFiletype(), '')})

  " See :help errorformat and :help errorformat-multi-line
  let errorformat = '%E%f:%l:%c: '      " Matches the file name, line number and column number
  let errorformat .= 'error:\ %m'       " Matches the error message
  let errorformat .= ',%C%p^,%Z'        " Matches the ^^^^ that points to the error
  
  " Note that we mark the errors as 'Style' errors; Syntastic can be configured to ignore these.
  return SyntasticMake({ 'makeprg': makeprg,
                        \'errorformat': errorformat,
                        \'subtype': 'Style',
                        \'Preprocess': 'Basenames_to_absolute_paths' })
endfunction

call g:SyntasticRegistry.CreateAndRegisterChecker({ 'filetype': 'cpp', 'name': 'lint381' })

let &cpo = s:save_cpo
unlet s:save_cpo
