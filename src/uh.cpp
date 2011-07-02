/******************************************************************************
 * Copyright 2011 Larry Olson
 *****************************************************************************/
#include <string>
#include <set>

#include "./IncludeHandler.h"

#include "llvm/ADT/SmallVector.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/Path.h"
#include "llvm/Support/Regex.h"
#include "llvm/Support/Host.h"

#include "clang/Frontend/Utils.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Basic/FileManager.h"
#include "clang/Lex/PPCallbacks.h"
#include "clang/Lex/PreProcessor.h"
#include "clang/Basic/SourceManager.h"
#include "clang/Lex/HeaderSearch.h"
#include "clang/Parse/ParseAST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/Basic/TargetOptions.h"
#include "clang/Basic/TargetInfo.h"
#include "clang/Rewrite/Rewriter.h"

using llvm::cl::opt;
using llvm::cl::desc;
using llvm::cl::init;
using llvm::cl::Positional;
using llvm::cl::Required;
using llvm::cl::list;
using llvm::cl::ParseCommandLineOptions;

using llvm::sys::Path;
using llvm::sys::PathWithStatus;
using llvm::sys::FileStatus;
using llvm::sys::path::extension;

using llvm::StringRef;

using clang::CompilerInstance;
using clang::TargetInfo;

/*
 * If this flag is specified, the tool will actually rename any headers that
 * match the specified header. The default value is false, which just causes
 * the tool to print where a header was found.
 */ 
static opt<bool>        Rename(
                               "rename",
                               desc("Renames any headers found"),
                               init(false));

static opt<std::string> Filename(
                               Positional,
                               desc("headerFilename"),
                               Required);

static opt<std::string> SearchDir(
                               Positional,
                               desc("[searchDir]"),
                               init(""));

// using llvm's list.
static list<std::string> IncludeDirs(
                               Positional,
                               desc("[includeDir]"));
/*
 * FORWARD DECLARATIONS
 */
void FindFilesContainingHeaders();
bool recurseDirectories(const Path&, std::set<Path>&, std::string*);

/*
 * main 
 */
int main(int argc, char **argv) {
    ParseCommandLineOptions(argc, argv,
        "Finds inconsistently named headers and shows their location.");
    if ( SearchDir.empty() ) {
        SearchDir = Path::GetCurrentDirectory().str();
    }
    FindFilesContainingHeaders();
    return 0;
}

/*
 * FindFilesContainingHeaders
 */
void FindFilesContainingHeaders() {
    std::set<std::string> candidateFiles;
    Path searchPath(SearchDir);

    std::set<Path> childPaths;
    std::string *errorMsg;

    recurseDirectories(searchPath, childPaths, errorMsg);
    std::set<Path>::iterator childIterator;

    /*
    for( childIterator = childPaths.begin(); childIterator != childPaths.end(); childIterator++)
    {
        std::cout << (*childIterator).str() << std::endl;
    }
    */

    clang::CompilerInstance ci;

    clang::HeaderSearchOptions hsos = ci.getHeaderSearchOpts();
    hsos.AddPath(SearchDir, clang::frontend::Quoted, false, false, false);

    for (int i = 0, e = IncludeDirs.size(); i != e; ++i) {
        hsos.AddPath(
            IncludeDirs[i],
            clang::frontend::Quoted,
            false,
            false,
            false);
    }

    ci.createFileManager();
    ci.createDiagnostics(0, NULL);

    clang::TargetOptions to;
    to.Triple = llvm::sys::getHostTriple();
    TargetInfo *pti = TargetInfo::CreateTargetInfo(ci.getDiagnostics(), to);
    ci.setTarget(pti);

    clang::ASTConsumer astConsumer;
    clang::LangOptions lOpts;

    for (childIterator = childPaths.begin();
         childIterator != childPaths.end();
         childIterator++) {
        ci.createSourceManager(ci.getFileManager());
        clang::SourceManager &sm = ci.getSourceManager();
        clang::Rewriter rw(sm, lOpts);

        ci.createPreprocessor();
        clang::Preprocessor &pp = ci.getPreprocessor();

        ci.createASTContext();

        uh::IncludeHandler *includeHandler = new uh::IncludeHandler(
            ci.getSourceManager(),
            *childIterator,
            Filename,
            rw,
            Rename);

        pp.addPPCallbacks(includeHandler);
        ci.setPreprocessor(&pp);

        clang::ApplyHeaderSearchOptions(
            pp.getHeaderSearchInfo(),
            hsos,
            lOpts,
            pti->getTriple());

        ci.InitializeSourceManager((*childIterator).str());
        ci.getDiagnosticClient().BeginSourceFile(lOpts, &pp);
        clang::ParseAST(pp , &astConsumer, ci.getASTContext());
        ci.getDiagnosticClient().EndSourceFile();
    }
}

/*
 * recurseDirectories - This function scans through
 * the Paths vector and replaces any directories it
 * finds with all the files in that directory (recursively). It uses the
 * sys::Path::getDirectoryContent method to perform the actual directory scans.
 */
bool recurseDirectories(const Path& path,
                   std::set<Path>& result,
                   std::string* ErrMsg) {
    // llvm::Regex candidateRegEx(".[hHcC][pP]?[pP]?");
    llvm::Regex candidateRegEx("\\.[hc]p?p?", llvm::Regex::IgnoreCase);
    llvm::SmallVector<StringRef, 1> matches;

    result.clear();
    std::set<Path> content;
    if (path.getDirectoryContents(content, ErrMsg))
        return true;
    for (std::set<Path>::iterator I = content.begin(), E = content.end();
         I != E;
         ++I) {
             // Make sure it exists and is a directory
             PathWithStatus PwS(*I);
             const FileStatus *Status = PwS.getFileStatus(false, ErrMsg);
             if (!Status)
                return true;
            if (Status->isDir) {
                std::set<Path> moreResults;
                if (recurseDirectories(*I, moreResults, ErrMsg))
                    return true;
                for (std::set<Path>::iterator II = moreResults.begin(),
                    EE = moreResults.end();
                    II != EE;
                    ++II) {
                    Path p = *II;
                    StringRef pString(p.str());
                    StringRef ext = extension(pString);
                    if (ext.size() > 0 && candidateRegEx.match(ext)) {
                        result.insert(*II);
                    }
                }
            } else {
                Path p = *I;
                StringRef pString(p.str());
                StringRef ext = extension(pString);
                if (ext.size() > 0 && candidateRegEx.match(ext)) {
                    result.insert(*I);
                }
            }
        }
    return false;
}
