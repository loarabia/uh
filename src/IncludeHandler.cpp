/******************************************************************************
 * Copyright 2011 Larry Olson
 *****************************************************************************/
#include <string>
#include <iostream>

#include "./IncludeHandler.h"
#include "llvm/Support/raw_ostream.h"

using uh::IncludeHandler;
using clang::PresumedLoc;
using clang::RewriteBuffer;

void IncludeHandler::InclusionDirective(SourceLocation hashLoc,
                                    const Token &includeTok,
                                    llvm::StringRef filename,
                                    bool isAngled,
                                    const FileEntry *file,
                                    SourceLocation endLoc,
                                    llvm::StringRef searchPath,
                                    llvm::StringRef relativePath) {
        if ((headerFilename.size() == filename.size())
            && headerRegex.match(filename)) {
             if (includesFoundInFile <= 0) {
                 std::cout << "Inside file:";
                 std::cout << fileBeingParsed.str() << std::endl;
                 std::cout << " found following includes:" << std::endl;
                 ++includesFoundInFile;
             }


             PresumedLoc loc = sm.getPresumedLoc(hashLoc);
             std::cout << "Start ";
             std::cout << loc.getColumn();
             std::cout << " ";
             loc = sm.getPresumedLoc(endLoc);
             std::cout << "End ";
             std::cout << loc.getColumn();
             std::cout << " Line ";
             std::cout << loc.getLine();
             std::cout << " ";
             std::cout << filename.str() << std::endl;

             if (rewrite) {
                 bool result = rewriter.ReplaceText(
                    endLoc.getFileLocWithOffset(1),
                    filename.size(),
                    headerFilename);

                 for (Rewriter::buffer_iterator I = rewriter.buffer_begin(),
                     E = rewriter.buffer_end();
                     I != E;
                     ++I) {
                     const FileEntry *fe =
                          rewriter.getSourceMgr().getFileEntryForID(I->first);
                      std::string Filename = fe->getName();
                      std::string Err;
                      llvm::raw_fd_ostream OS(Filename.c_str(), Err,
                                              llvm::raw_fd_ostream::F_Binary);
                      if (!Err.empty()) { }
                      RewriteBuffer &RewriteBuf = I->second;
                      RewriteBuf.write(OS);
                      OS.flush();
                 }
             }
        }
}
