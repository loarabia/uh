#include <iostream>

#include "IncludeHandler.h"

using namespace uh;

void IncludeHandler::InclusionDirective(SourceLocation hashLoc,
                                    const Token &includeTok,
                                    llvm::StringRef filename,
                                    bool isAngled,
                                    const FileEntry *file,
                                    SourceLocation endLoc,
                                    llvm::StringRef searchPath,
                                    llvm::StringRef relativePath)
{
        if( (headerFilename.size() == filename.size()) && headerRegex.match(filename))
        {
             if( includesFoundInFile <= 0)
             {
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
        }
}
