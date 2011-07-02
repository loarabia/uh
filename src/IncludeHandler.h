/******************************************************************************
 * Copyright 2011 Larry Olson
 *****************************************************************************/
#ifndef SRC_INCLUDEHANDLER_H_
#define SRC_INCLUDEHANDLER_H_

#include <string>

#include "clang/Basic/FileManager.h"
#include "clang/Basic/SourceManager.h"
#include "clang/Basic/SourceLocation.h"
#include "clang/Rewrite/Rewriter.h"
#include "clang/Lex/PPCallbacks.h"

#include "llvm/ADT/StringRef.h"
#include "llvm/Support/Path.h"
#include "llvm/Support/Regex.h"

using clang::PPCallbacks;
using clang::SourceManager;
using clang::Rewriter;
using clang::SourceLocation;
using clang::Token;
using clang::FileEntry;

namespace uh {
    class IncludeHandler : public PPCallbacks {
        const SourceManager &sm;
        llvm::sys::Path fileBeingParsed;
        int includesFoundInFile;
        llvm::Regex headerRegex;
        llvm::StringRef headerFilename;
        Rewriter rewriter;
        bool rewrite;

        public:
            IncludeHandler(const SourceManager &srcMgr,
                           llvm::sys::Path file,
                           std::string &header,
                           Rewriter &rw,
                           bool rewrite) :
                sm(srcMgr),
                fileBeingParsed(file),
                includesFoundInFile(0),
                headerRegex(header, llvm::Regex::IgnoreCase),
                headerFilename(header),
                rewriter(rw),
                rewrite(rewrite) { }

            void InclusionDirective(SourceLocation,
                                    const Token &,
                                    llvm::StringRef,
                                    bool,
                                    const FileEntry *,
                                    SourceLocation,
                                    llvm::StringRef,
                                    llvm::StringRef);
    };
}
#endif  // SRC_INCLUDEHANDLER_H_
