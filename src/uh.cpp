#include <iostream>
#include <string>
#include <vector>

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
#include "clang/Basic/FileManager.h"
#include "clang/Parse/ParseAST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/Basic/TargetOptions.h"
#include "clang/Basic/TargetInfo.h"


using namespace llvm;

class IncludeCallbackHandler: public clang::PPCallbacks
{
public:
    virtual void InclusionDirective(
                clang::SourceLocation hashMarkLocation,
                const clang::Token &includeToken,
                StringRef fileName,
                bool isAngled,
                const clang::FileEntry *file,
                clang::SourceLocation endLocation,
                StringRef searchPath,
                StringRef relativePath)
    {
        std::cout << fileName.str() << std::endl;
    }
};

/*
 * If this flag is specified, the tool will actually rename and headers that
 * match the specified header. The fefault value is false, which just causes
 * the tool to print where a header was found.
 */ 
static cl::opt<bool>        Rename(
								"rename",
								cl::desc("Renames any headers found"),
								cl::init(false));

static cl::opt<std::string> Filename(
								cl::Positional,
								cl::desc("headerFilename"),
								cl::Required);

static cl::opt<std::string> SearchDir(
								cl::Positional,
								cl::desc("[searchDir]"),
								cl::init(""));

/*
 * FORWARD DECLARATIONS
 */
std::set<sys::Path> FindFilesContainingHeaders();
bool recurseDirectories(const sys::Path&, std::set<sys::Path>&, std::string*);

/*
 * main 
 */
int main( int argc, char **argv)
{
	cl::ParseCommandLineOptions(argc, argv,
		"Finds inconsistently named headers and shows their location.");
    FindFilesContainingHeaders();
}

/*
 * FindFilesContainingHeaders
 */
std::set<sys::Path> FindFilesContainingHeaders()
{
    std::set<std::string> candidateFiles;
    sys::Path searchPath(SearchDir);

    std::set<sys::Path> childPaths;
    std::string *errorMsg;

    recurseDirectories(searchPath, childPaths, errorMsg);
    std::set<sys::Path>::iterator childIterator;

    for( childIterator = childPaths.begin(); childIterator != childPaths.end(); childIterator++)
    {
        std::cout << (*childIterator).str() << std::endl;
    }

    for( childIterator = childPaths.begin(); childIterator != childPaths.end(); childIterator++)
    {
        clang::CompilerInstance ci;

        clang::HeaderSearchOptions hsos = ci.getHeaderSearchOpts();
        hsos.AddPath(SearchDir, clang::frontend::Quoted, false, false, false); 
        hsos.AddPath("/Users/loarabia/Code/uh/test/scenarios/fakeproject", clang::frontend::Quoted,
            false, false, false);
        ci.createFileManager();
        ci.createDiagnostics(0, NULL);
        ci.createSourceManager(ci.getFileManager());

        clang::TargetOptions to;
        to.Triple = llvm::sys::getHostTriple();
        clang::TargetInfo *pti = clang::TargetInfo::CreateTargetInfo(ci.getDiagnostics(), to);
        ci.setTarget(pti);


        ci.createPreprocessor();
        ci.createASTContext();
        clang::Preprocessor &pp = ci.getPreprocessor();
        IncludeCallbackHandler *includeHandler = new IncludeCallbackHandler();
        pp.addPPCallbacks(includeHandler);
        ci.setPreprocessor(&pp);

        clang::ASTConsumer astConsumer;
        clang::LangOptions lOpts;

        clang::ApplyHeaderSearchOptions(
            pp.getHeaderSearchInfo(),
            hsos,
            lOpts,
            pti->getTriple());
        std::cout << (*childIterator).str() << std::endl;
        ci.getSourceManager().clearIDTables();
        ci.InitializeSourceManager( (*childIterator).str());
        ci.getDiagnosticClient().BeginSourceFile(lOpts, &pp);
        clang::ParseAST(pp , &astConsumer, ci.getASTContext());
        ci.getDiagnosticClient().EndSourceFile();
    }
}

/*
 * recurseDirectories - Implements the "R" modifier. This function scans through
 * the Paths vector and replaces any directories it
 * finds with all the files in that directory (recursively). It uses the
 * sys::Path::getDirectoryContent method to perform the actual directory scans.
 */
bool
recurseDirectories(const sys::Path& path,
                   std::set<sys::Path>& result,
                   std::string* ErrMsg)
{
    llvm::Regex candidateRegEx(".[hHcC][pP]?[pP]?");
    llvm::SmallVector<StringRef,1> matches;

    result.clear();
    std::set<sys::Path> content;
    if (path.getDirectoryContents(content, ErrMsg))
        return true;
    for (std::set<sys::Path>::iterator I = content.begin(), E = content.end();
         I != E;
         ++I) 
         {
             // Make sure it exists and is a directory
             sys::PathWithStatus PwS(*I);
             const sys::FileStatus *Status = PwS.getFileStatus(false, ErrMsg);
             if (!Status)
                return true;
            if (Status->isDir) {
                std::set<sys::Path> moreResults;
                if (recurseDirectories(*I, moreResults, ErrMsg))
                    return true;
                for( std::set<sys::Path>::iterator II = moreResults.begin(),
                    EE = moreResults.end();
                    II != EE;
                    ++II)
                {
                    sys::Path p = *II;
                    StringRef pString(p.str());
                    StringRef ext = sys::path::extension(pString);
                    if(candidateRegEx.match(ext))
                    {
                        result.insert(*II);
                    }
                    
                }
            } else {
                result.insert(*I);
            }
        }
    return false;
 }
 
