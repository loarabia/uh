#ifndef UH_INCLUDEHANDLER_H
#define UH_INCLUDEHANDLER_H

#include "clang/Basic/FileManager.h"
#include "clang/Basic/SourceManager.h"
#include "clang/Basic/SourceLocation.h"
#include "clang/Rewrite/Rewriter.h"
#include "clang/Lex/PPCallbacks.h"

#include "llvm/ADT/StringRef.h"
#include "llvm/Support/Path.h"
#include "llvm/Support/Regex.h"

using namespace clang;

namespace uh
{
    class IncludeHandler : public clang::PPCallbacks
    {
        SourceManager &sm;
        llvm::sys::Path fileBeingParsed;
        int includesFoundInFile;
        llvm::Regex headerRegex;
        llvm::StringRef headerFilename;
        clang::Rewriter rewriter;
        bool rewrite;

        public:
            IncludeHandler( SourceManager &srcMgr,
                            llvm::sys::Path file, 
                            std::string &header,
                            clang::Rewriter &rw,
                            bool rewrite) :
                sm(srcMgr),
                fileBeingParsed(file),
                includesFoundInFile(0),
                headerRegex(header, llvm::Regex::IgnoreCase),
                headerFilename(header),
                rewriter(rw),
                rewrite(rewrite)
                {
                }

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
#endif
