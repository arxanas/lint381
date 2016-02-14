;;; lint381.el --- style check your code according to EECS381 style guidelines

;;; Commentary:

;; This package allows you to filter code through lint381 to warn you about
;; potential violations of the EECS 381 style guidelines. This is done through
;; flycheck, so if you don't have that installed, get to that first.
;; see https://github.com/arxanas/lint381,
;;     http://www.umich.edu/~eecs381/handouts/C_Coding_Standards.pdf,
;; and http://www.umich.edu/~eecs381/handouts/C++_Coding_Standards.pdf

;; Ensure the directory of this file is in your `load-path' and add
;;
;;   (require 'lint381)
;;
;; to your .emacs configuration.

;; you will likely want to add a c-mode hook in which you define the language
;; used to be c. The following should suffice:
;;
;; (setq flycheck-lint381-language "c")

;;; Notes:
;; the writer of this file assumes that if you're using this, you're
;; probably also using cppcheck. if this is not the case, this may not work.
;; more to come on that

;;; Code:

(require 'flycheck)

(defgroup lint381 nil
  "Style check code using lint381."
  :group 'tools)

(flycheck-define-checker c/c++-lint381
  "A c++ style checker based on the lint381 tool.
See URL `https://github.com/arxanas/lint381'."
  :command ("lint381"
            (option "--lang=" flycheck-lint381-language concat)
            source)
  :error-patterns
  ((warning line-start (file-name) ":" line ":" column ": error: " (message)
            line-end))
  :modes (c++-mode c-mode))

(flycheck-def-option-var flycheck-lint381-language "cpp" c/c++-lint381
  "The language to use for the linter.
   Valid options are c and cpp , defaulting to cpp"
  :group 'clang-format
  :type 'string)
(make-variable-buffer-local 'flycheck-lint381-language)

(flycheck-add-next-checker 'c/c++-cppcheck '(warning . c/c++-lint381))
(add-to-list 'flycheck-checkers 'c/c++-lint381 'append)

(provide 'lint381)
